import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Red de Libros",
    page_icon="📚",
    layout="centered"
)

# TÍTULO PRINCIPAL
st.title("🏠 Bienvenido a Red de Libros")
st.markdown("""
Imagina un lugar donde los amantes de la lectura pueden conectarse, compartir sus libros favoritos
y descubrir nuevas historias juntos.  
¡Eso es exactamente lo que ofrecemos en **Red de Libros**! 📖✨

Aquí puedes crear tu perfil de lector, unirte a clubes de lectura, participar en discusiones literarias
y mucho más.

Ya seas un ávido lector o alguien que está buscando su próxima gran aventura literaria,
nuestra comunidad está aquí para ti.

¿Listo para comenzar tu viaje de lectura con nosotros? 🚀
""")

st.markdown("---")

# SECCIÓN QUIÉNES SOMOS (UNIDA)
st.header("Sobre el creador y la plataforma")
img_path = Path("/workspaces/mi-primera-app-streamlit/imagenes/quienes_somos/fotocreador.png")

col1, col2 = st.columns([1, 2])
with col1:
    if img_path.exists():
        st.image(str(img_path), width=220)
    else:
        st.warning("No se encuentra disponible la foto del creador.")
with col2:
    st.markdown("""
    "Hola, soy **Patricio Canales**, el creador de Red de Libros.  
    Soy un apasionado de la lectura. Esta plataforma nació de mi deseo
    de conectar con otros amantes de los libros y compartir nuestras experiencias literarias.
    Espero que disfrutes usando **Red de Libros** tanto como yo disfruté creándola."
    """)

st.markdown("---")

st.markdown("### ¿Por qué elegir Red de Libros?")
st.markdown("""
- **Comunidad Apasionada**: Únete a una red de lectores que comparten tu amor por los libros.
- **Descubrimiento Personalizado**: Recibe recomendaciones basadas en tus gustos literarios.
- **Interfaz Intuitiva**: Navega fácilmente y encuentra lo que buscas sin complicaciones.
""")
