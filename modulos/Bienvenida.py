import streamlit as st

def mostrar_bienvenida(nombre):
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)

    st.title(f"👋 Bienvenid@, {nombre}!")
    st.markdown("""
    Este sistema te permite consultar tus cursos:
                
    ---
    **¿Cómo usar el sistema?**
    - Usa el menú lateral para navegar entre los módulos.
    - Los cambios pueden tardar en actualizarse.

    ---
    **Versión:** Prueba 
    **Fecha:** 8/Agosto/2025
    **Desarrollado por el:** *El practicante de control de producion Ing.Cesar Armando Nuñez Alonso*  
    """)

