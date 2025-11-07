import streamlit as st
import sqlite3
import json
import ast
import time
from utils.google_books_api import buscar_libros  # asegúrate que exista esta función

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Perfil | Red de Libros", page_icon="📚", layout="wide")

# --- VERIFICAR SESIÓN ---
if "usuario" not in st.session_state:
    st.warning("🔒 Debes iniciar sesión primero para acceder a tu perfil.")
    st.stop()

usuario = st.session_state["usuario"]
user_id, nombre_usuario, correo = usuario[:3]

# --- CONEXIÓN A LA BASE DE DATOS ---
def conectar_db():
    return sqlite3.connect("data/usuarios.db", check_same_thread=False)

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
        # Intentar JSON
        try:
            return json.loads(campo)
        except json.JSONDecodeError:
            # Intentar AST
            try:
                lista = ast.literal_eval(campo)
                # Reescribir como JSON válido
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
    """Convierte strings antiguos en diccionarios válidos."""
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

# --- INTERFAZ ---
st.title(f"📖 Perfil de {nombre_usuario}")
st.markdown(f"**Correo:** {correo}")
st.divider()

# --- FUNCIÓN PARA MOSTRAR LIBRO EN FORMATO CASCADA ---
def mostrar_libro_cascada(libro, campo, idx):
    clave = f"{campo}_{idx}_{libro['titulo']}"
    with st.expander(f"{libro['titulo']} — {libro['autor']}"):
        st.image(libro.get("imagen", "https://via.placeholder.com/128x192?text=Sin+Imagen"), width=100)
        st.markdown(f"**Género:** {libro.get('genero', 'No especificado')}")
        st.markdown(f"**Editorial:** {libro.get('editorial', 'No especificada')}")
        st.markdown(f"**Descripción:** {libro.get('descripcion', 'Sin descripción disponible.')}")
        st.markdown(f"[📘 Ver en Google Books]({libro.get('link', '#')})")

        # --- REORDENAR ---
        if st.session_state.get("modo_reordenar", False):
            col_up, col_down = st.columns(2)
            if col_up.button("⬆️ Subir", key=f"up_{clave}"):
                lista = libros_gustados if campo == "libros_gustados" else libros_no_gustados
                if idx > 0:
                    lista[idx], lista[idx-1] = lista[idx-1], lista[idx]
                    st.rerun()
            if col_down.button("⬇️ Bajar", key=f"down_{clave}"):
                lista = libros_gustados if campo == "libros_gustados" else libros_no_gustados
                if idx < len(lista) - 1:
                    lista[idx], lista[idx+1] = lista[idx+1], lista[idx]
                    st.rerun()
        # --- ELIMINAR ---
        else:
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

st.divider()

# --- MODO CAMBIAR ORDEN ---
st.subheader("⚙️ Personalizar orden de tus libros")

if "modo_reordenar" not in st.session_state:
    st.session_state["modo_reordenar"] = False

if not st.session_state["modo_reordenar"]:
    if st.button("⚙️ Cambiar orden", use_container_width=True):
        st.session_state["modo_reordenar"] = True
        st.rerun()
else:
    st.info("Usa los botones ↑ ↓ para cambiar el orden de tus libros.")
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ Confirmar cambios", use_container_width=True):
            save_list_to_db("libros_gustados", libros_gustados)
            save_list_to_db("libros_no_gustados", libros_no_gustados)
            st.success("✔️ Cambios guardados exitosamente.")
            st.session_state["modo_reordenar"] = False
            time.sleep(0.5)
            st.rerun()
    with col_cancel:
        if st.button("❌ Cancelar", use_container_width=True):
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

# --- AÑADIR LIBRO MANUALMENTE ---
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

st.divider()

# --- ANÁLISIS DE GUSTOS ---
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
    st.info("Aún no hay suficientes datos para analizar tus gustos.")

st.divider()
st.header("💬 Mis publicaciones en el foro")
st.info("Aquí aparecerán tus posts cuando el foro esté habilitado.")
