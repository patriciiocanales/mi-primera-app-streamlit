import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Quiénes Somos",
    page_icon="👤", 
    layout="centered")

st.title("👤 Quiénes Somos")

img_path = Path("/workspaces/mi-primera-app-streamlit/imagenes/quienes_somos/fotocreador.png")

col1, col2 = st.columns([1, 2])
with col1:
    if img_path.exists():
        st.image(str(img_path), width=220)
    else:
        st.warning("No se encontró la imagen del creador.")
with col2:
    st.markdown("""
    Soy **dmerd**, un amante de la lectura, la cultura y la tecnología.  
    Este proyecto nació para conectar a lectores de todo el mundo 🌍.
    """)

st.markdown("---")
st.markdown("""
**Red de Libros** es una red social de lectura donde puedes compartir tus libros,
descubrir nuevas historias y conectar con personas que leen como tú. 📚
""")

st.caption("© 2025 Red de Libros")