import sqlite3
import json
import ast
import os

# Ruta de la base
db_path = "/workspaces/mi-primera-app-streamlit/data/usuarios.db"

# Función para intentar decodificar listas
def parsear_lista(valor):
    if not valor:
        return []
    try:
        data = json.loads(valor)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(valor)
        except Exception:
            return []
    if isinstance(data, list):
        return data
    return []

# Mostrar cada usuario en formato vertical
def mostrar_usuario(usuario):
    id_, nombre, correo, leidos, gustados, no_gustados = usuario

    leidos = parsear_lista(leidos)
    gustados = parsear_lista(gustados)
    no_gustados = parsear_lista(no_gustados)

    print("╔" + "═" * 70 + "╗")
    print(f"║ ID               │ {id_}")
    print(f"║ Nombre           │ {nombre}")
    print(f"║ Correo           │ {correo}")
    print(f"║ Libros leídos    │ {len(leidos)}")
    print(f"║ Libros gustados  │ {len(gustados)}")
    if gustados:
        for libro in gustados:
            titulo = libro.get("titulo") if isinstance(libro, dict) else str(libro)
            autor = libro.get("autor") if isinstance(libro, dict) and "autor" in libro else ""
            if autor:
                print(f"║    {titulo} — {autor}")
            else:
                print(f"║    {titulo}")
    print(f"║ Libros no gustados │ {len(no_gustados)}")
    if no_gustados:
        for libro in no_gustados:
            titulo = libro.get("titulo") if isinstance(libro, dict) else str(libro)
            autor = libro.get("autor") if isinstance(libro, dict) and "autor" in libro else ""
            if autor:
                print(f"║    {titulo} — {autor}")
            else:
                print(f"║    {titulo}")
    print("╚" + "═" * 70 + "╝\n")


# Verificar base y ejecutar
if not os.path.exists(db_path):
    print("⚠️ No se encontró la base de datos en:", db_path)
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, nombre_usuario, correo, libros_leidos, libros_gustados, libros_no_gustados
            FROM usuarios
        """)
        usuarios = cursor.fetchall()

        if not usuarios:
            print("⚠️ No hay usuarios registrados todavía.")
        else:
            print("\n📚 Usuarios registrados en Red de Libros:\n")
            for u in usuarios:
                mostrar_usuario(u)

    except sqlite3.Error as e:
        print("❌ Error al consultar la base de datos:", e)
    finally:
        conn.close()
