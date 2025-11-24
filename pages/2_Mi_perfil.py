import sys, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "utils"))
import streamlit as st
import sqlite3
import json
import ast
import time
from utils.google_books_api import buscar_libros
from streamlit_sortables import sort_items

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Perfil", page_icon="📚", layout="wide")

# --- VERIFICAR SESIÓN ---
if "usuario" not in st.session_state:
    st.warning(" Debes iniciar sesión primero para acceder a tu perfil.")
    st.stop()

usuario = st.session_state["usuario"]
user_id, nombre_usuario, correo = usuario[:3]

# --- CONEXIÓN A LA BASE DE DATOS ---
def conectar_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /pages
    ROOT_DIR = os.path.dirname(BASE_DIR)  # sube a /
    data_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    ruta_db = os.path.join(data_dir, "usuarios.db")
    return sqlite3.connect(ruta_db, check_same_thread=False)


# --- FUNCIONES AUXILIARES ---
def obtener_listas(user_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT libros_gustados, libros_no_gustados FROM usuarios WHERE id = ?", (user_id,))
    datos = c.fetchone()
    conn.close()

    def parsear_lista(campo, nombre_campo):
        if not campo:
            return []
        try:
            return json.loads(campo)
        except json.JSONDecodeError:
            try:
                lista = ast.literal_eval(campo)
                conn2 = conectar_db()
                c2 = conn2.cursor()
                c2.execute(f"UPDATE usuarios SET {nombre_campo} = ? WHERE id = ?", (json.dumps(lista), user_id))
                conn2.commit()
                conn2.close()
                return lista
            except Exception:
                return []

    libros_gustados = parsear_lista(datos[0], "libros_gustados") if datos else []
    libros_no_gustados = parsear_lista(datos[1], "libros_no_gustados") if datos else []
    return libros_gustados, libros_no_gustados

def save_list_to_db(campo, lista):
    conn = conectar_db()
    c = conn.cursor()
    c.execute(f"UPDATE usuarios SET {campo} = ? WHERE id = ?", (json.dumps(lista), user_id))
    conn.commit()
    conn.close()

def normalizar_libros(lista):
    libros_normalizados = []
    for item in lista:
        if isinstance(item, str):
            libros_normalizados.append({
                "titulo": item,
                "autor": "Desconocido",
                "editorial": "No especificada",
                "descripcion": "",
                "genero": "No especificado",
                "link": "#",
                "imagen": "https://via.placeholder.com/128x192?text=Sin+Imagen"
            })
        else:
            libros_normalizados.append(item)
    return libros_normalizados

# --- CARGAR DATOS ---
libros_gustados, libros_no_gustados = obtener_listas(user_id)
libros_gustados = normalizar_libros(libros_gustados)
libros_no_gustados = normalizar_libros(libros_no_gustados)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if "editar_perfil" not in st.session_state:
    st.session_state["editar_perfil"] = False
if "modo_reordenar" not in st.session_state:
    st.session_state["modo_reordenar"] = False

# --- CABECERA DEL PERFIL CON BANNER Y FOTO ---

def asegurar_columnas_perfil():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("PRAGMA table_info(usuarios)")
    columnas = [col[1] for col in c.fetchall()]
    if "foto_perfil" not in columnas:
        c.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT DEFAULT ''")
    if "banner_perfil" not in columnas:
        c.execute("ALTER TABLE usuarios ADD COLUMN banner_perfil TEXT DEFAULT ''")
    conn.commit()
    conn.close()

asegurar_columnas_perfil()

def obtener_perfil(user_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT nombre_usuario, correo, foto_perfil, banner_perfil FROM usuarios WHERE id = ?", (user_id,))
    fila = c.fetchone()
    conn.close()
    if fila:
        nombre, correo, foto, banner = fila
        return {
            "nombre": nombre or "@usuario",
            "correo": correo,
            "foto": foto or "https://placehold.co/150x150?text=Perfil",
            "banner": banner or "https://placehold.co/1500x500?text=Banner+de+usuario"
        }
    return {"nombre": "@usuario", "correo": "", "foto": "", "banner": ""}

def obtener_stats_seguidores(user_id):
    conn = conectar_db()
    c = conn.cursor()

    # Contar seguidores (usuarios que siguen a este)
    c.execute("SELECT COUNT(*) FROM follows WHERE followed_id = ?", (user_id,))
    seguidores = c.fetchone()[0]

    # Contar seguidos (usuarios que este sigue)
    c.execute("SELECT COUNT(*) FROM follows WHERE follower_id = ?", (user_id,))
    seguidos = c.fetchone()[0]

    conn.close()

    return seguidores, seguidos  # ← Corregido: quitado el return recursivo

def actualizar_perfil(user_id, nuevo_nombre, nueva_foto, nuevo_banner):
    if not nuevo_nombre.startswith("@"):
        nuevo_nombre = f"@{nuevo_nombre}"
    conn = conectar_db()
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET nombre_usuario = ?, foto_perfil = ?, banner_perfil = ? WHERE id = ?",
        (nuevo_nombre, nueva_foto, nuevo_banner, user_id)
    )
    conn.commit()
    conn.close()

perfil = obtener_perfil(user_id)

# ← Agregado: definir seguidores y seguidos después de obtener perfil
seguidores, seguidos = obtener_stats_seguidores(user_id)

# --- ESTILO VISUAL ---
st.markdown(
    """
    <style>
    .perfil-container {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
    }
    .banner {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border: none;
    }
    .foto-perfil {
        position: absolute;
        bottom: -50px;
        left: 40px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 2px solid black; /* más delgado y negro */
        object-fit: cover;
        background: #eee;
    }
    .info-perfil {
        margin-top: 70px;
        padding: 0 20px;
    }
    .nombre {
        font-size: 1.5rem;
        font-weight: 600;
    }
    .correo, .uuid {
        color: #666;
        font-size: 0.9rem;
    }
    .editar-btn {
        position: absolute;
        top: 15px;
        right: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- RENDER PERFIL ---
st.markdown('<div class="perfil-container">', unsafe_allow_html=True)
st.markdown(f'<img src="{perfil["banner"]}" class="banner">', unsafe_allow_html=True)

# Botón funcional en la esquina superior derecha
editar_col = st.columns([0.8, 0.2])[1]
with editar_col:
    if st.button("✏️ Editar perfil"):
        st.session_state["editar_perfil"] = True

st.markdown(f'<img src="{perfil["foto"]}" class="foto-perfil">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INFO DE PERFIL ---
st.markdown(
    f"""
    <div class="info-perfil">
        <div class="nombre">{perfil['nombre']}</div>
        <div class="correo">📧 {perfil['correo']}</div>
        <div class="uuid">UUID: <code>{user_id}</code></div>
        <div class="correo">👥 Seguidores: <b>{seguidores}</b> — Siguiendo: <b>{seguidos}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- MODO EDICIÓN ---
if st.session_state["editar_perfil"]:
    with st.expander("🪞 Editar perfil", expanded=True):
        nuevo_nombre = st.text_input("Nuevo nombre de usuario", value=perfil["nombre"].replace("@", ""))
        nueva_foto = st.text_input("Link de imagen de perfil", value=perfil["foto"])
        nuevo_banner = st.text_input("Link de banner", value=perfil["banner"])
        st.caption("💡 Sube tus imágenes a [Imgur](https://imgur.com/upload) y pega el link directo (.jpg o .png).")

        col_guardar, col_cancelar = st.columns(2)
        with col_guardar:
            if st.button("💾 Guardar cambios"):
                actualizar_perfil(user_id, nuevo_nombre.strip(), nueva_foto or "", nuevo_banner or "")
                st.session_state["editar_perfil"] = False
                st.success("✅ Perfil actualizado correctamente.")
                time.sleep(0.5)
                st.rerun()
        with col_cancelar:
            if st.button("❌ Cancelar"):
                st.session_state["editar_perfil"] = False
                st.rerun()

# --- FUNCIÓN PARA MOSTRAR LIBROS ---
def mostrar_libro_cascada(libro, campo, idx):
    clave = f"{campo}_{idx}_{libro['titulo']}"
    with st.expander(f"{libro['titulo']} — {libro['autor']}"):
        st.image(libro.get("imagen", "https://via.placeholder.com/128x192?text=Sin+Imagen"), width=100)
        st.markdown(f"**Género:** {libro.get('genero', 'No especificado')}")
        st.markdown(f"**Editorial:** {libro.get('editorial', 'No especificada')}")
        st.markdown(f"**Descripción:** {libro.get('descripcion', 'Sin descripción disponible.')}")
        st.markdown(f"[📘 Ver en Google Books]({libro.get('link', '#')})")

        if st.session_state.get(f"confirmar_eliminar_{clave}", False):
            st.warning(f"¿Seguro que quieres eliminar **{libro['titulo']}**?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sí, eliminar", key=f"sí_{clave}"):
                    lista = libros_gustados if campo == "libros_gustados" else libros_no_gustados
                    lista.remove(libro)
                    save_list_to_db(campo, lista)
                    st.success(f"'{libro['titulo']}' eliminado correctamente.")
                    st.session_state[f"confirmar_eliminar_{clave}"] = False
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar", key=f"cancelar_{clave}"):
                    st.session_state[f"confirmar_eliminar_{clave}"] = False
        else:
            if st.button("🗑️ Eliminar este libro", key=f"eliminar_{clave}"):
                st.session_state[f"confirmar_eliminar_{clave}"] = True

# --- SECCIONES DE LIBROS ---
if not st.session_state["modo_reordenar"]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💖 Libros que te gustaron")
        if libros_gustados:
            for idx, libro in enumerate(libros_gustados):
                mostrar_libro_cascada(libro, "libros_gustados", idx)
        else:
            st.info("Aún no has indicado qué libros te gustaron.")
    with col2:
        st.subheader("💢 Libros que no te gustaron")
        if libros_no_gustados:
            for idx, libro in enumerate(libros_no_gustados):
                mostrar_libro_cascada(libro, "libros_no_gustados", idx)
        else:
            st.info("Aún no has indicado qué libros no te gustaron.")
else:
    st.info("👉 Arrastra los libros para reordenarlos o moverlos entre listas (vertical).")

    gustados_items = {
        'header': '💖 Libros que te gustaron',
        'items': [libro["titulo"] for libro in libros_gustados]
    }
    no_gustados_items = {
        'header': '💢 Libros que no te gustaron',
        'items': [libro["titulo"] for libro in libros_no_gustados]
    }

    sorted_result = sort_items([gustados_items, no_gustados_items], multi_containers=True, direction="vertical")

    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ Confirmar cambios"):
            nuevos_gustados, nuevos_no_gustados = [], []

            for titulo in sorted_result[0]["items"]:
                for libro in libros_gustados + libros_no_gustados:
                    if libro["titulo"] == titulo:
                        nuevos_gustados.append(libro)

            for titulo in sorted_result[1]["items"]:
                for libro in libros_gustados + libros_no_gustados:
                    if libro["titulo"] == titulo:
                        nuevos_no_gustados.append(libro)

            save_list_to_db("libros_gustados", nuevos_gustados)
            save_list_to_db("libros_no_gustados", nuevos_no_gustados)
            st.success("✔️ Cambios guardados exitosamente.")
            st.session_state["modo_reordenar"] = False
            time.sleep(0.5)
            st.rerun()

    with col_cancel:
        if st.button("❌ Cancelar"):
            st.session_state["modo_reordenar"] = False
            st.rerun()

st.divider()

# --- BUSCAR Y AÑADIR LIBROS ---
st.header("➕ Añadir libro")

with st.expander("🔍 Buscar libro para añadir"):
    termino = st.text_input("Introduce título o autor:", placeholder="Ej: Cien años de soledad")
    if termino:
        resultados = buscar_libros(termino, max_results=5)
        if resultados:
            for i, libro in enumerate(resultados):
                with st.expander(f"{libro['titulo']} — {libro['autor']}"):
                    st.image(libro.get("imagen", "https://via.placeholder.com/128x192?text=Sin+Imagen"), width=100)
                    st.markdown(f"**Descripción:** {libro['descripcion']}")
                    st.markdown(f"**Género:** {libro['genero']}")
                    st.markdown(f"[Ver más en Google Books]({libro['link']})")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("💖 Me gustó", key=f"like_{i}_{libro['titulo']}"):
                            libros_gustados.append(libro)
                            save_list_to_db("libros_gustados", libros_gustados)
                            st.success(f"'{libro['titulo']}' añadido a tus libros gustados.")
                            time.sleep(0.5)
                            st.rerun()
                    with col_b:
                        if st.button("💢 No me gustó", key=f"dislike_{i}_{libro['titulo']}"):
                            libros_no_gustados.append(libro)
                            save_list_to_db("libros_no_gustados", libros_no_gustados)
                            st.warning(f"'{libro['titulo']}' añadido a tus libros no gustados.")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.warning("No se encontraron resultados. Puedes añadirlo manualmente abajo 👇")

# --- AÑADIR MANUALMENTE ---
with st.expander("✍️ Añadir libro manualmente"):
    with st.form("manual_add"):
        titulo_manual = st.text_input("Título del libro")
        autor_manual = st.text_input("Autor")
        genero_manual = st.text_input("Género o categoría")
        descripcion_manual = st.text_area("Descripción breve")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            gustar = st.form_submit_button("💖 Añadir a 'Me gustó'")
        with col_m2:
            no_gustar = st.form_submit_button("💢 Añadir a 'No me gustó'")

        if gustar and titulo_manual:
            nuevo_libro = {
                "titulo": titulo_manual,
                "autor": autor_manual or "Desconocido",
                "genero": genero_manual or "No especificado",
                "descripcion": descripcion_manual or "",
                "link": "#",
                "editorial": "No especificada",
                "imagen": "https://via.placeholder.com/128x192?text=Sin+Imagen"
            }
            libros_gustados.append(nuevo_libro)
            save_list_to_db("libros_gustados", libros_gustados)
            st.success(f"'{titulo_manual}' añadido a 'Me gustó'.")
            st.rerun()

        if no_gustar and titulo_manual:
            nuevo_libro = {
                "titulo": titulo_manual,
                "autor": autor_manual or "Desconocido",
                "genero": genero_manual or "No especificado",
                "descripcion": descripcion_manual or "",
                "link": "#",
                "editorial": "No especificada",
                "imagen": "https://via.placeholder.com/128x192?text=Sin+Imagen"
            }
            libros_no_gustados.append(nuevo_libro)
            save_list_to_db("libros_no_gustados", libros_no_gustados)
            st.warning(f"'{titulo_manual}' añadido a 'No me gustó'.")
            st.rerun()

# --- ANÁLISIS DE GUSTOS ---
st.divider()
st.header("📊 Análisis de tus gustos")
if libros_gustados:
    from collections import Counter
    autores = [libro.get("autor", "Desconocido") for libro in libros_gustados]
    editoriales = [libro.get("editorial", "Desconocida") for libro in libros_gustados]
    autor_fav = Counter(autores).most_common(1)[0][0]
    editorial_fav = Counter(editoriales).most_common(1)[0][0]
    st.success(f"💡 Te gustan especialmente los libros de **{autor_fav}**.")
    st.info(f"🏢 Sueles disfrutar libros publicados por **{editorial_fav}**.")
else:
    st.info("Añade libros a tu lista de 'Me gustó' para ver un análisis de tus gustos aquí.")

