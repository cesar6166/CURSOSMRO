import streamlit as st
from db.conexion import get_connection
from datetime import datetime

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
    cursos_resp = supabase.table("cursos").select("id_curso, nombre").execute()

    usuarios = usuarios_resp.data
    cursos = cursos_resp.data

    if usuarios and cursos:
        usuarios_dict = {f"{u['nombre']} (Ficha: {u['ficha']})": u['id_usuario'] for u in usuarios}
        cursos_dict = {c['nombre']: c['id_curso'] for c in cursos}

        usuario_seleccionado = st.selectbox("Selecciona un usuario:", list(usuarios_dict.keys()))
        curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))
        estado = st.selectbox("Estado del curso:", ["aprobado", "reprobado"])

        if estado != "Pendiente":
            fecha_realizacion = st.date_input("Fecha de realización del curso:")
            porcentaje = st.number_input("Porcentaje obtenido:", min_value=0.0, max_value=100.0, step=0.1)
        else:
            fecha_realizacion = None
            porcentaje = 0.0

        if st.button("Asignar Curso"):
            id_usuario = usuarios_dict[usuario_seleccionado]
            id_curso = cursos_dict[curso_seleccionado]

            # Verificar si ya existe el registro
            registro_resp = supabase.table("estado_cursos").select("id_estado").eq("id_usuario", id_usuario).eq("id_curso", id_curso).execute()
            registro_existente = registro_resp.data[0] if registro_resp.data else None

            if estado != "Pendiente" and fecha_realizacion > datetime.today().date():
                st.error("⚠️ La fecha de realización no puede ser futura.")
            else:
                fecha_str = fecha_realizacion.strftime("%Y-%m-%d") if fecha_realizacion else "2000-01-01"

                if registro_existente:
                    supabase.table("estado_cursos").update({
                        "fecha_realizacion": fecha_str,
                        "estado": estado,
                        "porcentaje": porcentaje
                    }).eq("id_estado", registro_existente["id_estado"]).execute()
                    st.success("✅ Curso actualizado exitosamente.")
                else:
                    supabase.table("estado_cursos").insert({
                        "id_usuario": id_usuario,
                        "id_curso": id_curso,
                        "fecha_realizacion": fecha_str,
                        "estado": estado,
                        "porcentaje": porcentaje
                    }).execute()
                    st.success("✅ Curso asignado exitosamente.")
