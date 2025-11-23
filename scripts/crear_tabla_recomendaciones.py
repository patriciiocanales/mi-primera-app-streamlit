import sqlite3

# Conexión a la base existente
conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

# Crear la tabla posts (si no existe, con el campo de categorías)
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT NOT NULL,
    contenido TEXT NOT NULL,
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    likes INTEGER DEFAULT 0,
    imagen_url TEXT DEFAULT '',
    libro_relacionado TEXT DEFAULT '',
    categorias TEXT DEFAULT '[]',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# Crear tabla follows
cursor.execute("""
CREATE TABLE IF NOT EXISTS follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id TEXT NOT NULL,
    followed_id TEXT NOT NULL,
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (follower_id) REFERENCES usuarios(id),
    FOREIGN KEY (followed_id) REFERENCES usuarios(id),
    UNIQUE(follower_id, followed_id)
)
""")

# 🔥 NUEVA TABLA PARA GUARDAR LIKES INDIVIDUALES
cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT NOT NULL,        -- el que dio like
    post_id INTEGER NOT NULL,        -- el post al que dio like
    fecha TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    UNIQUE(usuario_id, post_id)      -- evita que un usuario dé like dos veces al mismo post
)
""")

# Verificar si las columnas existen antes de agregarlas (para evitar errores en ejecuciones repetidas)
cursor.execute("PRAGMA table_info(usuarios)")
columnas = [col[1] for col in cursor.fetchall()]

if "seguidores_count" not in columnas:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN seguidores_count INTEGER DEFAULT 0")

if "seguidos_count" not in columnas:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN seguidos_count INTEGER DEFAULT 0")

conn.commit()
conn.close()

print("✅ Base de datos actualizada: posts con categorías, follows, y likes individuales creados correctamente.")
