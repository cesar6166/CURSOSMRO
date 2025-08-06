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

    st.header("Dar de Baja a un Usuario")

    # Obtener usuarios desde Supabase
    usuarios_resp = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute()
    usuarios = usuarios_resp.data

    if usuarios:
        usuarios_dict = {f"{u['nombre']} (Ficha: {u['ficha']})": u["id_usuario"] for u in usuarios}
        usuario_seleccionado = st.selectbox("Selecciona un usuario para eliminar:", list(usuarios_dict.keys()))
        id_usuario = usuarios_dict[usuario_seleccionado]

        st.warning("⚠️ Esta acción eliminará al usuario y todos sus cursos asignados.")
        confirmar = st.checkbox("Confirmo que deseo eliminar este usuario")

        if confirmar and st.button("Eliminar Usuario"):
            # Eliminar cursos asignados
            supabase.table("estado_cursos").delete().eq("id_usuario", id_usuario).execute()
            # Eliminar usuario
            supabase.table("usuarios").delete().eq("id_usuario", id_usuario).execute()
            st.success("✅ Usuario eliminado exitosamente.")
            st.rerun()
    else:
        st.info("No hay usuarios registrados.")
