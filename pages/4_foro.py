import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_cookies_controller import CookieController

# === CONFIGURACIONES PERSONALIZABLES DEL FEED ===
ancho_feed = 35
separacion_vertical = 124
altura_text_area = 100

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Red de Libros | Feed", layout="wide")
cookies = CookieController()

# === CONEXIÓN A LA BASE DE DATOS ===
conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT NOT NULL,
    contenido TEXT NOT NULL,
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    likes INTEGER DEFAULT 0,
    imagen_url TEXT DEFAULT '',
    libro_relacionado TEXT DEFAULT '',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")
conn.commit()

# === VERIFICAR SESIÓN ===
if "usuario" not in st.session_state:
    cookies_dict = cookies.getAll() or {}
    correo_cookie = cookies_dict.get("correo")
    if correo_cookie:
        cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo_cookie,))
        user = cursor.fetchone()
        if user:
            st.session_state["usuario"] = user

if "usuario" not in st.session_state:
    st.warning("⚠️ Debes iniciar sesión para ver y publicar en el feed.")
    st.stop()

usuario = st.session_state["usuario"]
usuario_id, nombre_usuario, correo = usuario[0], usuario[1], usuario[2]

# Obtener foto_perfil directamente de la base de datos para asegurar que esté actualizada
cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = ?", (usuario_id,))
result = cursor.fetchone()
foto_perfil = result[0] if result and result[0] else "https://via.placeholder.com/50"

# === ICONOS ===
def icon_placeholder(icon_name):
    icons = {
        "home": "🏠", "friends": "👥", "messages": "💬", "notifications": "🔔",
        "cart": "🛒", "profile": "👤", "settings": "⚙️", "photo": "📷",
        "video": "🎥", "gif": "🎞️", "like": "👍", "comment": "💬",
        "save": "💾", "repost": "🔄", "search": "🔍",
    }
    return icons.get(icon_name, "❓")

# === CSS GLOBAL ===
st.markdown(f"""
<style>
body {{
    background-color: #1b2230;
    color: white;
    font-family: "Segoe UI", sans-serif;
}}
.logo {{ font-size: 24px; font-weight: bold; }}
.nav-icons {{ display: flex; gap: 10px; }}
.profile {{ display: flex; align-items: center; gap: 5px; }}

.section-wrapper {{
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
    transition: background 0.3s ease;
}}
.section-wrapper:hover {{ background: rgba(255, 255, 255, 0.08); }}

.item-card {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 15px 20px;
    margin-bottom: {separacion_vertical}px;
    transition: background 0.3s ease, transform 0.2s ease;
    width: 100%;
    max-width: 600px;
    margin: 15px auto;
}}
.item-card:hover {{
    background: rgba(255,255,255,0.1);
    transform: translateY(-2px);
}}
.feed-avatar {{ border-radius: 50%; }}
.subheader {{
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 12px;
}}
hr {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin: {separacion_vertical}px 0;
}}

/* ====== CONTENEDOR DE POSTS ====== */
.feed-container {{
    max-width: 650px;
    margin: 0 auto;
}}

/* ====== IMÁGENES Y VIDEOS ====== */
.post-media {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 6px;
    margin-bottom: 6px;
}}
.post-media img {{
    border-radius: 8px;
    width: 225px;
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}}

/* ====== SECCIÓN DE LIKES ====== */
.likes-section {{
    text-align: left;
    opacity: 0.85;
    font-size: 14px;
    margin-top: 6px;  /* separación mínima con la imagen */
}}
</style>
""", unsafe_allow_html=True)

# === LAYOUT PRINCIPAL ===
col_left, col_center, col_right = st.columns([2, 5, 2])

# === COLUMNA IZQUIERDA ===
with col_left:
    st.markdown('<div class="subheader">🕮 Últimos Posts Visitados</div>', unsafe_allow_html=True)
    recent_posts = cursor.execute("SELECT contenido, fecha FROM posts ORDER BY id DESC LIMIT 2").fetchall()
    for post in recent_posts:
        st.markdown(f"""
        <div class="item-card">
            <b>{post[0][:35]}...</b><br>
            <span style="opacity:0.7;font-size:13px;">{post[1]}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="subheader">👥 Quienes Sigues (16)</div>', unsafe_allow_html=True)
    following_avatars = ["https://via.placeholder.com/50" for _ in range(8)]
    cols = st.columns(4)
    for i, avatar in enumerate(following_avatars):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="item-card" style="text-align:center;">
                <img src="{avatar}" width="50" class="feed-avatar">
            </div>
            """, unsafe_allow_html=True)

# === COLUMNA CENTRAL ===
with col_center:
    st.markdown(f'<div class="subheader">📚 Bienvenido, {nombre_usuario}</div>', unsafe_allow_html=True)

    # === NUEVO POST ===
    st.markdown("**Comparte algo con la comunidad...**")
    col_prof, col_text = st.columns([1, 4])

    with col_prof:
        # Usar HTML img para mostrar la imagen de perfil de manera consistente y evitar errores
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="{foto_perfil}" alt="{nombre_usuario}" width="80" class="feed-avatar">
            <br><small style="color: white;">{nombre_usuario}</small>
        </div>
        """, unsafe_allow_html=True)

    with col_text:
        contenido = st.text_area("", placeholder="¿Qué estás pensando?", height=altura_text_area)
        imagen_url = st.text_input(f"{icon_placeholder('photo')} Link de imagen / video / GIF (opcional)")
        libro_relacionado = st.text_input("📖 Libro relacionado (opcional)")
        if st.button("Publicar"):
            if not contenido.strip():
                st.warning("⚠️ El post no puede estar vacío.")
            else:
                cursor.execute("""
                    INSERT INTO posts (usuario_id, contenido, imagen_url, libro_relacionado)
                    VALUES (?, ?, ?, ?)
                """, (usuario_id, contenido, imagen_url, libro_relacionado))
                conn.commit()
                st.success("✅ Post publicado correctamente.")
                st.rerun()

    # === FEED ===
    col_spacer1, col_feed, col_spacer2 = st.columns([1, ancho_feed, 1])
    with col_feed:
        tab1, tab2, tab3 = st.tabs(["Descubrir", "Siguiendo", "Tendencias"])

        cursor.execute("""
            SELECT p.id, u.nombre_usuario, u.foto_perfil, p.contenido, 
                   p.imagen_url, p.libro_relacionado, p.fecha, p.likes
            FROM posts p
            JOIN usuarios u ON p.usuario_id = u.id
            ORDER BY datetime(p.fecha) DESC
        """)
        posts = cursor.fetchall()

        for pid, nombre, foto_perfil, contenido, img, libro, fecha, likes in posts:
            st.markdown(f"""
            <div class="item-card">
                <div style="display:flex;gap:10px;align-items:center;margin-bottom:4px;">
                    <img src="{foto_perfil if foto_perfil else 'https://via.placeholder.com/50'}" 
                         width="50" class="feed-avatar">
                    <div>
                        <b>{nombre}</b><br>
                        <span style="font-size:13px;opacity:0.7;">{fecha}</span>
                    </div>
                </div>
                <div style="margin-top:0px;">{contenido}</div>
            """, unsafe_allow_html=True)

            # === Media (dentro del item-card) ===
            if img:
                if any(ext in img.lower() for ext in [".mp4", ".webm"]):
                    st.markdown(f"""
                    <div class="post-media">
                        <video controls width="100%">
                            <source src="{img}" type="video/mp4">
                        </video>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="post-media">
                        <img src="{img}">
                    </div>
                    """, unsafe_allow_html=True)

            # === Libro ===
            if libro:
                st.markdown(f"📖 <i>Relacionado con:</i> <b>{libro}</b>", unsafe_allow_html=True)

            # === Likes ===
            st.markdown(f"<div class='likes-section'>👍 {likes} likes</div>", unsafe_allow_html=True)

            # === Cerramos item-card recién aquí ===
            st.markdown("</div><hr>", unsafe_allow_html=True)

# === COLUMNA DERECHA ===
with col_right:
    st.markdown('<div class="subheader">🔍 Buscar Tema, Libro o Autor</div>', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="Buscar...")
    if st.button("Buscar"):
        st.info(f"Buscando: {search_query}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="subheader">Actividad de Amigos</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="item-card">📘 <b>Adele</b> publicó un nuevo post</div>
    <div class="item-card">💬 <b>Mike</b> comentó en una publicación</div>
    """, unsafe_allow_html=True)

# === CIERRE DE CONEXIÓN ===
conn.close()
