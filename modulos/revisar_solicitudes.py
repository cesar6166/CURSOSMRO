import streamlit as st
import pandas as pd
from db.conexion import get_connection
from datetime import date, datetime

supabase = get_connection()

def mostrar_solicitudes():
    st.header("📥 Solicitudes de Aprobación de Cursos")

    # Obtener usuarios y cursos
    usuarios_resp = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute().data
    cursos_resp = supabase.table("cursos").select("id_curso, nombre").execute().data

    usuarios_dict = {u["id_usuario"]: u for u in usuarios_resp}
    cursos_dict = {c["id_curso"]: c for c in cursos_resp}

    # Filtro por ficha
    fichas = sorted(set(u["ficha"] for u in usuarios_resp))
    ficha_seleccionada = st.selectbox("Filtrar por ficha de usuario (opcional):", ["Todos"] + fichas)

    # Obtener solicitudes pendientes
    solicitudes_query = supabase.table("solicitudes_aprobacion").select("*").eq("estado_solicitud", "pendiente")
    if ficha_seleccionada != "Todos":
        usuario_filtrado = next((u for u in usuarios_resp if u["ficha"] == ficha_seleccionada), None)
        if usuario_filtrado:
            solicitudes_query = solicitudes_query.eq("id_usuario", usuario_filtrado["id_usuario"])
    solicitudes = solicitudes_query.execute().data

    if not solicitudes:
        st.info("✅ No hay solicitudes pendientes.")
        return

    for solicitud in solicitudes:
        id_solicitud = solicitud["id_solicitud"]
        id_usuario = solicitud["id_usuario"]
        id_curso = solicitud["id_curso"]

        usuario = usuarios_dict.get(id_usuario, {})
        curso = cursos_dict.get(id_curso, {})

        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(f"""
            **Usuario:** {usuario.get("nombre", "Desconocido")}  
            **Ficha:** {usuario.get("ficha", "N/A")}  
            **Curso:** {curso.get("nombre", "Desconocido")}  
            **Fecha de solicitud:** {solicitud.get("fecha_solicitud", "N/A")}  
            **Comentario:** {solicitud.get("comentario_usuario", "—")}
            """)

        with col2:
            fecha_realizacion = st.date_input(
                f"Fecha de realización ({curso.get('nombre', '')})",
                key=f"fecha_{id_solicitud}",
                value=date.today()
            )

            if st.button("✅ Aprobar", key=f"aprobar_{id_solicitud}"):
                # Actualizar estado del curso
                supabase.table("estado_cursos").update({
                    "estado": "aprobado",
                    "fecha_realizacion": fecha_realizacion.isoformat()
                }).eq("id_usuario", id_usuario).eq("id_curso", id_curso).execute()

                # Actualizar solicitud
                supabase.table("solicitudes_aprobacion").update({
                    "estado_solicitud": "aprobada",
                    "fecha_respuesta": date.today().isoformat(),
                    "respuesta_admin": "Curso aprobado manualmente"
                }).eq("id_solicitud", id_solicitud).execute()

                st.success("✅ Solicitud aprobada.")

            if st.button("❌ Rechazar", key=f"rechazar_{id_solicitud}"):
                supabase.table("solicitudes_aprobacion").update({
                    "estado_solicitud": "rechazada",
                    "fecha_respuesta": date.today().isoformat(),
                    "respuesta_admin": "Solicitud rechazada"
                }).eq("id_solicitud", id_solicitud).execute()
                st.warning("❌ Solicitud rechazada.")
