import streamlit as st
from db.conexion import get_connection
from datetime import datetime, timedelta

supabase = get_connection()

def mostrar():
    # Encabezado con logos
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)
        
    st.header("Asignar Curso a Usuario")

    usuarios_resp = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute()
    cursos_resp = supabase.table("cursos").select("id_curso, nombre, frecuencia").execute()

    usuarios = usuarios_resp.data
    cursos = cursos_resp.data

    if usuarios and cursos:
        usuarios_dict = {f"{u['nombre']} (Ficha: {u['ficha']})": u['id_usuario'] for u in usuarios}
        cursos_dict = {c['nombre']: c for c in cursos}

        usuario_seleccionado = st.selectbox("Selecciona un usuario:", list(usuarios_dict.keys()))
        curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))
        estado = st.selectbox("Estado del curso:", ["aprobado", "reprobado"])

        fecha_realizacion = None
        porcentaje = 0.0

        if estado == "aprobado":
            fecha_vencimiento = st.date_input("Fecha de vencimiento del curso:")
            porcentaje = 100.0

            curso = cursos_dict[curso_seleccionado]
            frecuencia = curso.get("frecuencia", "anual").lower()

            if frecuencia == "anual":
                fecha_realizacion = fecha_vencimiento - timedelta(days=365)
            elif frecuencia == "semestral":
                fecha_realizacion = fecha_vencimiento - timedelta(days=180)
            elif frecuencia == "trimestral":
                fecha_realizacion = fecha_vencimiento - timedelta(days=90)
            else:
                fecha_realizacion = fecha_vencimiento - timedelta(days=365)  # por defecto

            st.info(f"📅 Fecha de realización calculada: {fecha_realizacion.strftime('%Y-%m-%d')}")

        if st.button("Asignar Curso"):
            id_usuario = usuarios_dict[usuario_seleccionado]
            id_curso = cursos_dict[curso_seleccionado]["id_curso"]

            registro_resp = supabase.table("estado_cursos").select("id_estado").eq("id_usuario", id_usuario).eq("id_curso", id_curso).execute()
            registro_existente = registro_resp.data[0] if registro_resp.data else None

            fecha_str = fecha_realizacion.strftime("%Y-%m-%d") if fecha_realizacion else None

            datos = {
                "id_usuario": id_usuario,
                "id_curso": id_curso,
                "estado": estado,
                "porcentaje": porcentaje
            }

            if fecha_str:
                datos["fecha_realizacion"] = fecha_str

            if registro_existente:
                supabase.table("estado_cursos").update(datos).eq("id_estado", registro_existente["id_estado"]).execute()
                st.success("✅ Curso actualizado exitosamente.")
            else:
                supabase.table("estado_cursos").insert(datos).execute()
                st.success("✅ Curso asignado exitosamente.")
