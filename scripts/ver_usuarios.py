import sqlite3
import json
import ast
import os

# Ruta de la base
db_path = "data/usuarios.db"

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
def mostrar_usuario(usuario, columnas_disponibles):
    # Desempaquetar según las columnas disponibles
    id_ = usuario[0]
    nombre = usuario[1]
    correo = usuario[2]
    leidos = parsear_lista(usuario[3])
    gustados = parsear_lista(usuario[4])
    no_gustados = parsear_lista(usuario[5])
    
    # Verificar si posts_count y fecha_creacion existen
    posts_count = usuario[6] if len(usuario) > 6 and "posts_count" in columnas_disponibles else "N/A (columna no existe)"
    fecha_creacion = usuario[7] if len(usuario) > 7 and "fecha_creacion" in columnas_disponibles else "N/A (columna no existe)"

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
    print(f"║ Posts publicados │ {posts_count}")
    print(f"║ Fecha creación   │ {fecha_creacion}")
    print("╚" + "═" * 70 + "╝\n")

# Verificar base y ejecutar
if not os.path.exists(db_path):
    print("⚠️ No se encontró la base de datos en:", db_path)
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar columnas disponibles en usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas_disponibles = [col[1] for col in cursor.fetchall()]
        
        # Construir la consulta dinámicamente
        columnas_a_consultar = ["id", "nombre_usuario", "correo", "libros_leidos", "libros_gustados", "libros_no_gustados"]
        if "posts_count" in columnas_disponibles:
            columnas_a_consultar.append("posts_count")
        if "fecha_creacion" in columnas_disponibles:
            columnas_a_consultar.append("fecha_creacion")
        
        query = f"SELECT {', '.join(columnas_a_consultar)} FROM usuarios"
        cursor.execute(query)
        usuarios = cursor.fetchall()

        if not usuarios:
            print("⚠️ No hay usuarios registrados todavía.")
        else:
            print("\n📚 Usuarios registrados en Red de Libros:\n")
            for u in usuarios:
                mostrar_usuario(u, columnas_disponibles)

    except sqlite3.Error as e:
        print("❌ Error al consultar la base de datos:", e)
    finally:
        conn.close()