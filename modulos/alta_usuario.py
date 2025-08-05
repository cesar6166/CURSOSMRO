import streamlit as st
from db.conexion import get_connection

conn = get_connection()
cursor = conn.cursor()

def mostrar():
    # Encabezado con logos
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)
        
    st.header("Alta de Usuarios")
    nombre_usuario = st.text_input("Nombre del usuario:")
    ficha_usuario = st.text_input("Número de ficha:")
    rol_usuario = st.selectbox("Rol del usuario:", ["usuario", "administrador"])

    if st.button("Registrar Usuario"):
        if nombre_usuario and ficha_usuario and rol_usuario:
            try:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, ficha, rol) VALUES (?, ?, ?)",
                    (nombre_usuario, ficha_usuario, rol_usuario)
                )
                conn.commit()
                st.success("✅ Usuario registrado exitosamente.")
            except:
                st.error("⚠️ La ficha ya está registrada.")
        else:
            st.warning("Por favor, completa todos los campos.")
