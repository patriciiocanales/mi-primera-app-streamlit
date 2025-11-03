import sqlite3
from tabulate import tabulate

# Conexión a la base de datos
conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

# Mostrar todos los usuarios registrados
cursor.execute("SELECT id, nombre_usuario, correo, libros_leidos, libros_gustados, libros_no_gustados FROM usuarios")
usuarios = cursor.fetchall()

if usuarios:
    print("\n📚 Usuarios registrados en Red de Libros:\n")
    print(tabulate(
        usuarios,
        headers=["ID", "Nombre", "Correo", "Libros leídos", "Libros gustados", "Libros no gustados"],
        tablefmt="fancy_grid"
    ))
else:
    print("⚠️ No hay usuarios registrados todavía.")

conn.close()
