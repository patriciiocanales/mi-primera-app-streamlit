import streamlit as st
import sqlite3
import json
import ast
import time
from utils.google_books_api import buscar_libros
from streamlit_sortables import sort_items

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Perfil de Usuario", page_icon="📚", layout="wide")

# --- VERIFICAR SESIÓN ---
if "usuario" not in st.session_state:
    st.warning(" Debes iniciar sesión primero para acceder a perfiles.")
    st.stop()

# Nota: No usamos usuario logueado para mostrar datos; solo para verificar sesión.

# === OBTENER EL ID DEL USUARIO A VER ===
user_id = st.session_state.get("usuario_id_a_ver")
if not user_id:
    st.error("No se seleccionó un perfil válido. Redirigiendo al foro...")
    st.switch_page("pages/4_foro.py")

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

# --- BUSCAR DATOS DEL USUARIO A MOSTRAR ---
conn = conectar_db()
c = conn.cursor()
c.execute("SELECT nombre_usuario, correo, foto_perfil, banner_perfil FROM usuarios WHERE id = ?", (user_id,))
fila = c.fetchone()
conn.close()
if not fila:
    st.error("Usuario no encontrado. Redirigiendo al foro...")
    st.switch_page("pages/4_foro.py")

nombre_usuario, correo, foto_perfil, banner_perfil = fila
foto_perfil = foto_perfil or "https://placehold.co/150x150?text=Perfil"
banner_perfil = banner_perfil or "https://placehold.co/1500x500?text=Banner+de+usuario"

# --- FUNCIÓN PARA OBTENER STATS DE SEGUIDORES ---
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

    return seguidores, seguidos

# --- OBTENER STATS ---
seguidores, seguidos = obtener_stats_seguidores(user_id)

# --- CARGAR DATOS ---
libros_gustados, libros_no_gustados = obtener_listas(user_id)
libros_gustados = normalizar_libros(libros_gustados)
libros_no_gustados = normalizar_libros(libros_no_gustados)

# --- OBTENER ID DEL USUARIO LOGUEADO ---
mi_id = st.session_state["usuario"][0]  # Asumiendo que usuario es una tupla (id, nombre, correo)

# --- FUNCIÓN PARA VERIFICAR SI YA SIGO ---
def verificar_si_sigo(mi_id, user_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?", (mi_id, user_id))
    existe = c.fetchone()
    conn.close()
    return existe is not None

# --- FUNCIONES SEGUIR / DEJAR DE SEGUIR ---
def seguir(mi_id, user_id):
    conn = conectar_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO follows (follower_id, followed_id) VALUES (?, ?)", (mi_id, user_id))
    except:
        pass
    conn.commit()
    conn.close()

def dejar_de_seguir(mi_id, user_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?", (mi_id, user_id))
    conn.commit()
    conn.close()

# --- BOTÓN DE VOLVER AL FORO (SUPER ARRIBA, EXTREMO IZQUIERDO) ---
col_volver, _ = st.columns([0.1, 0.9])
with col_volver:
    if st.button("← Volver al Foro"):
        st.switch_page("pages/4_foro.py")

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
        border: 2px solid black;
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
    </style>
    """,
    unsafe_allow_html=True
)

# --- RENDER PERFIL ---
st.markdown('<div class="perfil-container">', unsafe_allow_html=True)
st.markdown(f'<img src="{banner_perfil}" class="banner">', unsafe_allow_html=True)
st.markdown(f'<img src="{foto_perfil}" class="foto-perfil">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INFO DE PERFIL ---
st.markdown(
    f"""
    <div class="info-perfil">
        <div class="nombre">{nombre_usuario}</div>
        <div class="correo">📧 {correo}</div>
        <div class="uuid">UUID: <code>{user_id}</code></div>
        <div class="correo">👥 Seguidores: <b>{seguidores}</b> — Siguiendo: <b>{seguidos}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- BOTÓN SEGUIR / DEJAR DE SEGUIR ---
# No mostrar botón al ver tu propio perfil
if mi_id != user_id:
    sigo = verificar_si_sigo(mi_id, user_id)

    col_btn, _ = st.columns([0.25, 0.75])
    with col_btn:
        if not sigo:
            if st.button("💚 Seguir usuario"):
                seguir(mi_id, user_id)
                st.rerun()
        else:
            if st.button("💔 Dejar de seguir"):
                dejar_de_seguir(mi_id, user_id)
                st.rerun()

# --- FUNCIÓN PARA MOSTRAR LIBROS (SOLO VISUALIZACIÓN) ---
def mostrar_libro_cascada(libro):
    with st.expander(f"{libro['titulo']} — {libro['autor']}"):
        st.image(libro.get("imagen", "https://via.placeholder.com/128x192?text=Sin+Imagen"), width=100)
        st.markdown(f"**Género:** {libro.get('genero', 'No especificado')}")
        st.markdown(f"**Editorial:** {libro.get('editorial', 'No especificada')}")
        st.markdown(f"**Descripción:** {libro.get('descripcion', 'Sin descripción disponible.')}")
        st.markdown(f"[📘 Ver en Google Books]({libro.get('link', '#')})")

# --- SECCIONES DE LIBROS (SOLO VISUALIZACIÓN) ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("💖 Libros que le gustaron")
    if libros_gustados:
        for libro in libros_gustados:
            mostrar_libro_cascada(libro)
    else:
        st.info("Aún no ha indicado qué libros le gustaron.")
with col2:
    st.subheader("💢 Libros que no le gustaron")
    if libros_no_gustados:
        for libro in libros_no_gustados:
            mostrar_libro_cascada(libro)
    else:
        st.info("Aún no ha indicado qué libros no le gustaron.")

# --- ANÁLISIS DE GUSTOS ---
st.divider()
st.header("📊 Análisis de sus gustos")
if libros_gustados:
    from collections import Counter
    autores = [libro.get("autor", "Desconocido") for libro in libros_gustados]
    editoriales = [libro.get("editorial", "Desconocida") for libro in libros_gustados]
    autor_fav = Counter(autores).most_common(1)[0][0]
    editorial_fav = Counter(editoriales).most_common(1)[0][0]
    st.success(f"💡 Le gustan especialmente los libros de **{autor_fav}**.")
    st.info(f"🏢 Suele disfrutar libros publicados por **{editorial_fav}**.")
else:
    st.info("Aún no hay suficientes datos para analizar sus gustos.")

# --- FORO ---
st.divider()
st.header("💬 Sus publicaciones en el foro")

def obtener_posts_usuario(user_id):
    conn = conectar_db()
    c = conn.cursor()
    c.execute("""
        SELECT contenido, fecha, imagen_url, libro_relacionado, likes
        FROM posts
        WHERE usuario_id = ?
        ORDER BY datetime(fecha) DESC
    """, (user_id,))
    posts = c.fetchall()
    conn.close()
    return posts

posts_usuario = obtener_posts_usuario(user_id)

# --- ESTILO VISUAL IGUAL AL FORO ---
st.markdown("""
<style>
.item-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 15px 20px;
    margin-bottom: 12px;
    transition: background 0.3s ease, transform 0.2s ease;
    color: white;
}
.item-card:hover {
    background: rgba(255,255,255,0.1);
    transform: translateY(-2px);
}
.feed-avatar {
    border-radius: 50%;
}
</style>
""", unsafe_allow_html=True)

if not posts_usuario:
    st.info("Aún no ha publicado nada en el foro.")
else:
    for contenido, fecha, imagen, libro, likes in posts_usuario:
        st.markdown(
            f"""
            <div class="item-card">
                <div style="display:flex;gap:10px;align-items:center;">
                    <img src="{foto_perfil}" width="50" class="feed-avatar">
                    <div>
                        <b>{nombre_usuario}</b><br>
                        <span style="font-size:13px;opacity:0.7;">{fecha}</span>
                    </div>
                </div>
                <div style="margin-top:8px;">{contenido}</div>
            """,
            unsafe_allow_html=True
        )

        # --- Imagen o video del post ---
        if imagen:
            if any(ext in imagen for ext in [".mp4", ".webm"]):
                st.video(imagen)
            else:
                st.image(imagen, width=225)

        # --- Libro relacionado ---
        if libro:
            st.markdown(f"📖 <i>Relacionado con:</i> <b>{libro}</b>", unsafe_allow_html=True)

        # --- Likes ---
        st.markdown(f"<div style='opacity:0.8;margin-top:5px;'>👍 {likes} likes</div>", unsafe_allow_html=True)
        st.markdown("</div><hr>", unsafe_allow_html=True)