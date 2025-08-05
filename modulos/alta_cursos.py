import streamlit as st
from db.conexion import get_connection

def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    st.header("Alta de Cursos")
    nombre_curso = st.text_input("Nombre del curso:")
    frecuencia_curso = st.selectbox("Frecuencia del curso:", ["anual", "bienal", "trienal", "unico"])
    modalidad_curso = st.selectbox("Modalidad del curso:", ["pendiente", "presencial", "online"])

    if st.button("Registrar Curso"):
        if nombre_curso and frecuencia_curso and modalidad_curso:
            cursor.execute(
                "INSERT INTO cursos (nombre, frecuencia, modalidad) VALUES (?, ?, ?)",
                (nombre_curso, frecuencia_curso, modalidad_curso)
            )
            conn.commit()
            st.success("✅ Curso registrado exitosamente.")
        else:
            st.warning("Por favor, completa todos los campos.")

    st.divider()

    st.header("Modificar Curso Existente")
    cursos = cursor.execute("SELECT id_curso, nombre FROM cursos").fetchall()
    if cursos:
        cursos_dict = {f"{c[1]} (ID: {c[0]})": c[0] for c in cursos}
        curso_seleccionado = st.selectbox("Selecciona un curso para modificar:", list(cursos_dict.keys()))
        id_curso = cursos_dict[curso_seleccionado]

        nuevo_nombre = st.text_input("Nuevo nombre del curso:")
        nueva_frecuencia = st.selectbox("Nueva frecuencia:", ["anual", "bienal", "trienal", "unico"])
        nueva_modalidad = st.selectbox("Nueva modalidad:", ["pendiente", "presencial", "online"])

        if st.button("Guardar cambios"):
            if nuevo_nombre and nueva_frecuencia and nueva_modalidad:
                cursor.execute("""
                    UPDATE cursos
                    SET nombre = ?, frecuencia = ?, modalidad = ?
                    WHERE id_curso = ?
                """, (nuevo_nombre, nueva_frecuencia, nueva_modalidad, id_curso))
                conn.commit()
                st.success("✅ Curso modificado exitosamente.")
            else:
                st.warning("Por favor, completa todos los campos.")
    else:
        st.info("No hay cursos registrados aún.")
