import sqlite3
from tabulate import tabulate
import os

# Ruta a la base de datos (sube un nivel desde /scripts)
db_path = ("/workspaces/mi-primera-app-streamlit/data/usuarios.db")

# Verificar que la base de datos exista
if not os.path.exists(db_path):
    print("⚠️ No se encontró la base de datos en:", db_path)
    print("Asegúrate de que 'usuarios.db' esté en la carpeta 'data/'.")
else:
    # Conexión a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Mostrar todos los usuarios registrados
        cursor.execute("""
            SELECT id, nombre_usuario, correo, libros_leidos, libros_gustados, libros_no_gustados
            FROM usuarios
        """)
        usuarios = cursor.fetchall()

        if usuarios:
            print("\n📚 Usuarios registrados en Red de Libros:\n")
            print(tabulate(
                usuarios,
                headers=[
                    "ID", "Nombre", "Correo",
                    "Libros leídos", "Libros gustados", "Libros no gustados"
                ],
                tablefmt="fancy_grid"
            ))
        else:
            print("⚠️ No hay usuarios registrados todavía.")
    except sqlite3.Error as e:
        print("❌ Error al consultar la base de datos:", e)
    finally:
        conn.close()
