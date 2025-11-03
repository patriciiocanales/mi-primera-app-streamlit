import streamlit as st
import sqlite3
import hashlib
import uuid

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Login | Red de Libros", page_icon="🔐", layout="centered")

# --- CONEXIÓN A LA BASE DE DATOS ---
conn = sqlite3.connect("data/usuarios.db")
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    nombre_usuario TEXT,
    correo TEXT UNIQUE,
    contrasena TEXT,
    libros_leidos TEXT,
    libros_gustados TEXT,
    libros_no_gustados TEXT
)
""")
conn.commit()

# --- FUNCIONES AUXILIARES ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(correo, contrasena):
    cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
    user = cursor.fetchone()
    if user and user[3] == hash_password(contrasena):
        return user
    return None

# --- INTERFAZ ---
st.title("🔐 Inicia sesión o crea tu cuenta")
st.markdown("Bienvenido a **Red de Libros**, tu espacio para compartir y descubrir lecturas.")

opcion = st.radio("Selecciona una opción:", ["Iniciar sesión", "Registrarse"])

# --- LOGIN EXISTENTE ---
if opcion == "Iniciar sesión":
    correo = st.text_input("Correo electrónico")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        usuario = verificar_usuario(correo, contrasena)
        if usuario:
            st.success(f"✅ Bienvenido de nuevo, {usuario[1]}!")
            st.session_state["usuario"] = usuario
        else:
            st.error("❌ Credenciales incorrectas o usuario no registrado.")

# --- REGISTRO NUEVO ---
else:
    st.subheader("🆕 Crear nueva cuenta")
    nombre_usuario = st.text_input("Nombre de usuario")
    correo = st.text_input("Correo electrónico")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Registrarme"):
        if not nombre_usuario or not correo or not contrasena:
            st.warning("Completa todos los campos.")
        else:
            try:
                id_unico = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO usuarios (id, nombre_usuario, correo, contrasena,
                                          libros_leidos, libros_gustados, libros_no_gustados)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_unico,
                    nombre_usuario,
                    correo,
                    hash_password(contrasena),
                    "",
                    "",
                    ""
                ))
                conn.commit()
                st.success("🎉 Cuenta creada con éxito. ¡Ya puedes iniciar sesión!")
            except sqlite3.IntegrityError:
                st.error("⚠️ Ese correo ya está registrado.")

# --- CIERRE DE CONEXIÓN ---
conn.close()
