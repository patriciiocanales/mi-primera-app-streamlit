import sqlite3

conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recomendaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id TEXT,
    titulo TEXT,
    autor TEXT,
    descripcion TEXT,
    link TEXT,
    isbn TEXT,
    genero TEXT,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
""")

conn.commit()
conn.close()
print("✅ Tabla 'recomendaciones' creada correctamente.")
