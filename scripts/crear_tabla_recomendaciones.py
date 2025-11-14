import sqlite3

# Conexión a la base existente
conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

# Crear la tabla posts
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
conn.close()
print("✅ Tabla 'posts' creada correctamente.")
