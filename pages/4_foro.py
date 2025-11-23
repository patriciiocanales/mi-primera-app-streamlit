import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_cookies_controller import CookieController

# === CONFIGURACIONES PERSONALIZABLES DEL FEED ===
ancho_feed = 35
separacion_vertical = 124
altura_text_area = 100

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Red de libros | Foro", layout="wide")
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

# Agregar tabla para likes (para toggle)
cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    UNIQUE(usuario_id, post_id)
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
    st.warning("⚠️ Debes iniciar sesión para ver y publicar en el foro.")
    st.stop()

usuario = st.session_state["usuario"]
usuario_id, nombre_usuario, correo = usuario[0], usuario[1], usuario[2]

# Obtener foto_perfil directamente de la base de datos para asegurar que esté actualizada
cursor.execute("SELECT foto_perfil FROM usuarios WHERE id = ?", (usuario_id,))
result = cursor.fetchone()
foto_perfil = result[0] if result and result[0] else "https://via.placeholder.com/50"

# Obtener lista de usuarios seguidos (una vez para reutilizar)
cursor.execute("SELECT followed_id FROM follows WHERE follower_id = ?", (usuario_id,))
seguidos_ids = [row[0] for row in cursor.fetchall()]

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
    margin-bottom: 18px;
    transition: background 0.3s ease, transform 0.2s ease;
    width: 100%;
    display: block;
}}
.item-card:hover {{
    background: rgba(255,255,255,0.12);
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
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
</style>
""", unsafe_allow_html=True)

# === FUNCIÓN PARA RENDERIZAR POSTS (evita duplicación) ===
def render_posts(posts, tab_key):
    for pid, autor_id, nombre, foto, contenido, img, libro, fecha, likes in posts:
        # Verificar si el usuario dio like
        cursor.execute("SELECT id FROM likes WHERE usuario_id = ? AND post_id = ?", (usuario_id, pid))
        liked = cursor.fetchone() is not None

        st.markdown("<div class='item-card'>", unsafe_allow_html=True)

        # Encabezado (avatar + nombre + botón perfil)
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(f'<img src="{foto}" width="50" class="feed-avatar">', unsafe_allow_html=True)
        with col2:
            if st.button(nombre, key=f"perfil_{tab_key}_{pid}"):
                st.session_state["usuario_id_a_ver"] = autor_id
                st.switch_page("pages/5_perfil_de_usuario.py")
            st.markdown(f"<span style='font-size:13px;opacity:0.7;'>{fecha}</span>", unsafe_allow_html=True)

        # Contenido del post
        st.markdown(contenido, unsafe_allow_html=True)

        # Imagen o video si existe
        if img:
            if any(ext in img.lower() for ext in [".mp4", ".webm"]):
                st.video(img)
            else:
                st.image(img, width=225)

        # Libro relacionado si existe
        if libro:
            st.markdown(f"📖 <i>Relacionado con:</i> <b>{libro}</b>", unsafe_allow_html=True)

        # Likes y botón like
        col_likes, col_button = st.columns([3, 2])
        with col_likes:
            st.markdown(f"<div class='likes-section'>👍 {likes} likes</div>", unsafe_allow_html=True)
        with col_button:
            if liked:
                if st.button("💔 Quitar like", key=f"unlike_{tab_key}_{pid}"):
                    cursor.execute("DELETE FROM likes WHERE usuario_id = ? AND post_id = ?", (usuario_id, pid))
                    cursor.execute("UPDATE posts SET likes = likes - 1 WHERE id = ?", (pid,))
                    conn.commit()
                    st.rerun()
            else:
                if st.button("❤️ Me gusta", key=f"like_{tab_key}_{pid}"):
                    cursor.execute("INSERT OR IGNORE INTO likes (usuario_id, post_id) VALUES (?, ?)", (usuario_id, pid))
                    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (pid,))
                    conn.commit()
                    st.rerun()

        st.markdown("</div><hr>", unsafe_allow_html=True)

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

    # Título con conteo real
    st.markdown(f'<div class="subheader">👥 Quienes Sigues ({len(seguidos_ids)})</div>', unsafe_allow_html=True)

    if not seguidos_ids:
        st.info("Aún no sigues a nadie. ¡Empieza a seguir usuarios!")
    else:
        max_avatares = min(3, len(seguidos_ids))
        seguidos_ids_limited = seguidos_ids[:max_avatares]

        placeholders = ",".join("?" * len(seguidos_ids_limited))
        query = f"""
            SELECT id, nombre_usuario, foto_perfil
            FROM usuarios
            WHERE id IN ({placeholders})
        """
        cursor.execute(query, seguidos_ids_limited)
        seguidos = cursor.fetchall()

        if seguidos:
            avatar_cols = st.columns(1)
            for i, (followed_id, nombre, foto) in enumerate(seguidos):
                if not foto:
                    cursor.execute("""
                        SELECT imagen_url FROM posts
                        WHERE usuario_id = ? AND imagen_url != ''
                        ORDER BY id DESC LIMIT 1
                    """, (followed_id,))
                    post_img = cursor.fetchone()
                    foto_url = post_img[0] if post_img else "https://via.placeholder.com/50"
                else:
                    foto_url = foto

                with avatar_cols[0]:
                    st.markdown(
                        f"""
                        <div style='text-align:center; margin-bottom:12px;'>
                            <img src='{foto_url}' width='60' class='feed-avatar'
                                style='border:2px solid rgba(255,255,255,0.3); border-radius:50%;'>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# === COLUMNA CENTRAL ===
with col_center:
    st.markdown(f'<div class="subheader">📚 Bienvenido, {nombre_usuario}</div>', unsafe_allow_html=True)

    # === NUEVO POST ===
    st.markdown("**Comparte algo con la comunidad...**")
    col_prof, col_text = st.columns([1, 4])

    with col_prof:
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
                st.success("✅ Post publicado correctamente")
                st.rerun()

    # === FEED ===
    col_spacer1, col_feed, col_spacer2 = st.columns([1, ancho_feed, 1])
    with col_feed:
        tab1, tab2, tab3 = st.tabs(["Descubrir", "Siguiendo", "Tendencias"])

        with tab1:  # === DESCUBRIR ===
            cursor.execute("""
                SELECT p.id, u.id AS autor_id, u.nombre_usuario, u.foto_perfil,
                       p.contenido, p.imagen_url, p.libro_relacionado,
                       p.fecha, p.likes
                FROM posts p
                JOIN usuarios u ON p.usuario_id = u.id
                ORDER BY datetime(p.fecha) DESC
            """)
            posts = cursor.fetchall()
            render_posts(posts, "desc")

        with tab2:  # === SIGUIENDO ===
            if not seguidos_ids:
                st.info("Para ver publicaciones aquí, comienza a seguir a otros usuarios.")
            else:
                placeholders = ",".join("?" * len(seguidos_ids))
                query = f"""
                    SELECT p.id, u.id AS autor_id, u.nombre_usuario, u.foto_perfil,
                           p.contenido, p.imagen_url, p.libro_relacionado,
                           p.fecha, p.likes
                    FROM posts p
                    JOIN usuarios u ON p.usuario_id = u.id
                    WHERE p.usuario_id IN ({placeholders})
                    ORDER BY datetime(p.fecha) DESC
                """
                cursor.execute(query, seguidos_ids)
                posts = cursor.fetchall()

                if not posts:
                    st.info("Las personas que sigues aún no han publicado nada.")
                else:
                    render_posts(posts, "seg")

        with tab3:  # === TENDENCIAS ===
            st.write("Contenido para Tendencias (igual que Descubrir por ahora)")

# === COLUMNA DERECHA ===
with col_right:
    st.markdown('<div class="subheader">🔍 Buscar Tema, Libro o Autor</div>', unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="Buscar...")
    if st.button("Buscar"):
        st.info(f"Buscando: {search_query}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="subheader">Actividad de Amigos</div>', unsafe_allow_html=True)

    # Botón para refrescar manualmente la actividad
    if st.button("🔄 Refrescar Actividad", key="refresh_actividad"):
        st.rerun()

    if not seguidos_ids:
        st.info("Aún no sigues a nadie. ¡Empieza a seguir usuarios para ver su actividad!")
    else:
        placeholders = ",".join("?" * len(seguidos_ids))
        query_union = f"""
        SELECT * FROM (
            SELECT 'post' AS tipo, u.nombre_usuario, p.fecha, p.contenido
            FROM posts p
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.usuario_id IN ({placeholders})

            UNION ALL

            SELECT 'like' AS tipo, u.nombre_usuario, l.fecha, p.contenido
            FROM likes l
            JOIN usuarios u ON l.usuario_id = u.id
            JOIN posts p ON l.post_id = p.id
            WHERE l.usuario_id IN ({placeholders})
        )
        ORDER BY datetime(fecha) DESC
        LIMIT 30
        """
        # Parámetros: seguidos_ids dos veces (una para posts, una para likes)
        params = seguidos_ids + seguidos_ids
        cursor.execute(query_union, params)
        actividades = cursor.fetchall()

        if not actividades:
            st.info("Tus amigos aún no han publicado ni dado likes.")
        else:
            for tipo, actor, fecha, contenido in actividades:
                icon = "📝" if tipo == "post" else "❤️"
                accion = "publicó un post" if tipo == "post" else "le dio like a un post"
                preview = (contenido[:80] + "...") if contenido else "Sin contenido"
                st.markdown(f"""
                <div class="item-card" style="padding:12px; border-radius:10px; margin-bottom:10px;">
                    <b>{icon} @{actor}</b> {accion}<br>
                    <span style='opacity:0.8;'>{preview}</span><br>
                    <span style='opacity:0.6;font-size:12px;'>{fecha}</span>
                </div>
                """, unsafe_allow_html=True)

# === FIN DEL CÓDIGO ===