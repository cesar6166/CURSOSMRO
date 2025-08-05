import streamlit as st
from db.conexion import get_connection

def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    st.header("Dar de Baja Curso a Usuario")

    usuarios = cursor.execute("SELECT id_usuario, nombre, ficha FROM usuarios").fetchall()

    if usuarios:
        usuarios_dict = {f"{u[1]} (Ficha: {u[2]})": u[0] for u in usuarios}
        usuario_seleccionado = st.selectbox("Selecciona un usuario:", list(usuarios_dict.keys()))
        id_usuario = usuarios_dict[usuario_seleccionado]

        cursos_usuario = cursor.execute("""
            SELECT ec.id_estado, c.nombre
            FROM estado_cursos ec
            JOIN cursos c ON ec.id_curso = c.id_curso
            WHERE ec.id_usuario = ?
        """, (id_usuario,)).fetchall()

        if cursos_usuario:
            cursos_dict = {c[1]: c[0] for c in cursos_usuario}
            curso_a_eliminar = st.selectbox("Selecciona el curso a dar de baja:", list(cursos_dict.keys()))
            id_estado = cursos_dict[curso_a_eliminar]

            if st.button("Dar de Baja Curso"):
                cursor.execute("DELETE FROM estado_cursos WHERE id_estado = ?", (id_estado,))
                conn.commit()
                st.success("✅ Curso dado de baja exitosamente.")
        else:
            st.info("Este usuario no tiene cursos asignados.")
    else:
        st.warning("No hay usuarios registrados.")
