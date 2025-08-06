import streamlit as st
from db.conexion import get_connection
supabase = get_connection()

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
            # Verificar si la ficha ya existe
            existe = supabase.table("usuarios").select("id_usuario").eq("ficha", ficha_usuario).execute()
            if existe.data:
                st.error("⚠️ La ficha ya está registrada.")
            else:
                # Insertar nuevo usuario sin especificar el ID
                data = {
                    "nombre": nombre_usuario,
                    "ficha": ficha_usuario,
                    "rol": rol_usuario
                }
                supabase.table("usuarios").insert(data).execute()
                st.success("✅ Usuario registrado exitosamente.")
        else:
            st.warning("Por favor, completa todos los campos.")
