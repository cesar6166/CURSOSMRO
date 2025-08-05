import streamlit as st
from db.conexion import get_connection
from datetime import datetime

def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    st.header("Asignar Curso a Usuario")

    usuarios = cursor.execute("SELECT id_usuario, nombre, ficha FROM usuarios").fetchall()
    cursos = cursor.execute("SELECT id_curso, nombre FROM cursos").fetchall()

    if usuarios and cursos:
        usuarios_dict = {f"{u[1]} (Ficha: {u[2]})": u[0] for u in usuarios}
        cursos_dict = {c[1]: c[0] for c in cursos}

        usuario_seleccionado = st.selectbox("Selecciona un usuario:", list(usuarios_dict.keys()))
        curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))
        estado = st.selectbox("Estado del curso:", ["Pendiente", "realizado", "aprobado", "reprobado"])

        if estado != "Pendiente":
            fecha_realizacion = st.date_input("Fecha de realización del curso:")
        else:
            fecha_realizacion = None

        if st.button("Asignar Curso"):
            id_usuario = usuarios_dict[usuario_seleccionado]
            id_curso = cursos_dict[curso_seleccionado]

            cursor.execute("""
                SELECT id_estado FROM estado_cursos
                WHERE id_usuario = ? AND id_curso = ?
            """, (id_usuario, id_curso))
            registro_existente = cursor.fetchone()

            if estado != "Pendiente" and fecha_realizacion > datetime.today().date():
                st.error("⚠️ La fecha de realización no puede ser futura.")
            else:
                fecha_str = fecha_realizacion.strftime("%Y-%m-%d") if fecha_realizacion else "2000-01-01"

                if registro_existente:
                    cursor.execute("""
                        UPDATE estado_cursos
                        SET fecha_realizacion = ?, estado = ?
                        WHERE id_estado = ?
                    """, (fecha_str, estado, registro_existente[0]))
                    st.success("✅ Curso actualizado para el usuario.")
                else:
                    cursor.execute("""
                        INSERT INTO estado_cursos (id_usuario, id_curso, fecha_realizacion, estado)
                        VALUES (?, ?, ?, ?)
                    """, (id_usuario, id_curso, fecha_str, estado))
                    st.success("✅ Curso asignado exitosamente.")
                conn.commit()
