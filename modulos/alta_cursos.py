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
        
    st.header("Alta de Cursos")
    nombre_curso = st.text_input("Nombre del curso:")
    frecuencia_curso = st.selectbox("Frecuencia del curso:", ["anual", "bienal", "trienal", "unico"])
    modalidad_curso = st.selectbox("Modalidad del curso:", ["pendiente", "presencial", "online"])

    if st.button("Registrar Curso"):
        if nombre_curso and frecuencia_curso and modalidad_curso:
            data = {
                "nombre": nombre_curso,
                "frecuencia": frecuencia_curso,
                "modulo": modalidad_curso
            }
            supabase.table("cursos").insert(data).execute()
            st.success("✅ Curso registrado exitosamente.")
        else:
            st.warning("Por favor, completa todos los campos.")

    st.divider()

    st.header("Modificar Curso Existente")
    response = supabase.table("cursos").select("id_curso, nombre").execute()
    cursos = response.data

    if cursos:
        cursos_dict = {f"{c['nombre']} (ID: {c['id_curso']})": c['id_curso'] for c in cursos}
        curso_seleccionado = st.selectbox("Selecciona un curso para modificar:", list(cursos_dict.keys()))
        id_curso = cursos_dict[curso_seleccionado]

        nuevo_nombre = st.text_input("Nuevo nombre del curso:")
        nueva_frecuencia = st.selectbox("Nueva frecuencia:", ["anual", "bienal", "trienal", "unico"])
        nueva_modalidad = st.selectbox("Nueva modalidad:", ["pendiente", "presencial", "online"])

        if st.button("Guardar cambios"):
            if nuevo_nombre and nueva_frecuencia and nueva_modalidad:
                update_data = {
                    "nombre": nuevo_nombre,
                    "frecuencia": nueva_frecuencia,
                    "modulo": nueva_modalidad
                }
                supabase.table("cursos").update(update_data).eq("id_curso", id_curso).execute()
                st.success("✅ Curso modificado exitosamente.")
            else:
                st.warning("Por favor, completa todos los campos.")
    else:
        st.info("No hay cursos registrados aún.")
