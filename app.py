# ...existing code...
import streamlit as st

# Título de la app
st.title("¡Mi primera app!")
st.header("Encabezado")
st.subheader("Subencabezado")
st.write("Texto normal")
st.markdown("**Texto en negrita** o *cursiva*") 

# Texto simple
st.write("Hola, soy [TU NOMBRE] y esta es mi primera aplicación con Streamlit.")

# Un input interactivo
nombre = st.text_input("¿Cómo te llamas?")

# Respuesta condicional
if nombre:
    st.write(f"¡Hola, {nombre}! Bienvenido/a a mi app")

# Un botón
if st.button("Presiona aquí"):
    st.balloons()  # Animación de globos
    st.success("¡Funciona perfectamente!")

# Inputs del usuario (variable renombrada para no sobrescribir 'nombre')
texto = st.text_input("Escribe algo") 

edad = st.number_input("¿Cuántos años tienes?", min_value=0, max_value=120, step=1)

opcion = st.selectbox("Elige una opción", ["A", "B", "C"])

acepto = st.checkbox("Acepto los términos")

# Botón y acciones (mensajes dentro de la condición)
if st.button("Click aquí"):
    st.write("¡Botón presionado!")
    st.info(f"Has escrito: {texto}")
    if not acepto:
        st.warning("Debes aceptar los términos para continuar")
    else:
        st.success("Formulario enviado con éxito ✅")
# ...existing code...
