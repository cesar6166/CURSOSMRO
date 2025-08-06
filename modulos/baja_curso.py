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
        
    st.header("Dar de Baja Curso a Usuario")

    usuarios_resp = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute()
    usuarios = usuarios_resp.data

    if usuarios:
        usuarios_dict = {f"{u['nombre']} (Ficha: {u['ficha']})": u['id_usuario'] for u in usuarios}
        usuario_seleccionado = st.selectbox("Selecciona un usuario:", list(usuarios_dict.keys()))
        id_usuario = usuarios_dict[usuario_seleccionado]

        cursos_resp = supabase.table("estado_cursos").select("id_estado, id_curso").eq("id_usuario", id_usuario).execute()
        cursos_usuario = cursos_resp.data

        if cursos_usuario:
            cursos_info = supabase.table("cursos").select("id_curso, nombre").execute().data
            cursos_dict_full = {c["id_curso"]: c["nombre"] for c in cursos_info}

            cursos_dict = {
                cursos_dict_full.get(c["id_curso"], "Curso desconocido"): c["id_estado"]
                for c in cursos_usuario
            }

            curso_a_eliminar = st.selectbox("Selecciona el curso a dar de baja:", list(cursos_dict.keys()))
            id_estado = cursos_dict[curso_a_eliminar]

            if st.button("Dar de Baja Curso"):
                supabase.table("estado_cursos").delete().eq("id_estado", id_estado).execute()
                st.success("✅ Curso dado de baja exitosamente.")
        else:
            st.info("Este usuario no tiene cursos asignados.")
    else:
        st.warning("No hay usuarios registrados.")
