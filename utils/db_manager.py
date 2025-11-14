import sqlite3
import uuid

DB_PATH = "data/usuarios.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def crear_post(usuario_id, contenido, imagen_url="", libro_relacionado=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (usuario_id, contenido, imagen_url, libro_relacionado)
        VALUES (?, ?, ?, ?)
    """, (usuario_id, contenido, imagen_url, libro_relacionado))
    conn.commit()
    conn.close()

def obtener_posts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, u.nombre_usuario, u.foto_perfil, p.contenido, p.fecha, p.likes, p.imagen_url
        FROM posts p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.id DESC
    """)
    posts = cursor.fetchall()
    conn.close()
    return posts

def crear_usuario(nombre_usuario, correo, contrasena):
    conn = get_connection()
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO usuarios (id, nombre_usuario, correo, contrasena)
        VALUES (?, ?, ?, ?)
    """, (user_id, nombre_usuario, correo, contrasena))
    conn.commit()
    conn.close()
    return user_id
