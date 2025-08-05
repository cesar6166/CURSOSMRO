import streamlit as st
from db.conexion import get_connection

def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    # Encabezado con logos
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)
        
    st.header("Dar de Baja a un Usuario")

    usuarios = cursor.execute("SELECT id_usuario, nombre, ficha FROM usuarios").fetchall()

    if usuarios:
        usuarios_dict = {f"{u[1]} (Ficha: {u[2]})": u[0] for u in usuarios}
        usuario_seleccionado = st.selectbox("Selecciona un usuario para eliminar:", list(usuarios_dict.keys()))
        id_usuario = usuarios_dict[usuario_seleccionado]

        st.warning("⚠️ Esta acción eliminará al usuario y todos sus cursos asignados.")
        confirmar = st.checkbox("Confirmo que deseo eliminar este usuario")

        if confirmar and st.button("Eliminar Usuario"):
            # Eliminar cursos asignados primero
            cursor.execute("DELETE FROM estado_cursos WHERE id_usuario = ?", (id_usuario,))
            # Luego eliminar el usuario
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            conn.commit()
            st.success("✅ Usuario eliminado exitosamente.")
            st.rerun()
    else:
        st.info("No hay usuarios registrados.")
