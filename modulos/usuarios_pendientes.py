import streamlit as st
import pandas as pd
from db.conexion import get_connection

supabase = get_connection()

def mostrar_usuarios_pendientes():
    st.subheader("🔍 Usuarios con curso pendiente")

    cursos_resp = supabase.table("cursos").select("id_curso, nombre").execute()
    cursos_dict = {c["nombre"]: c["id_curso"] for c in cursos_resp.data}

    curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))

    if curso_seleccionado:
        id_curso = cursos_dict[curso_seleccionado]
        pendientes_resp = supabase.table("estado_cursos").select(
            "id_usuario, estado, fecha_realizacion, porcentaje"
        ).eq("id_curso", id_curso).neq("estado", "aprobado").execute()

        pendientes_data = pendientes_resp.data
        if pendientes_data:
            usuarios_info = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute().data
            usuarios_dict = {u["id_usuario"]: u for u in usuarios_info}

            df_pendientes = pd.DataFrame(pendientes_data)
            df_pendientes["nombre"] = df_pendientes["id_usuario"].apply(lambda uid: usuarios_dict.get(uid, {}).get("nombre", ""))
            df_pendientes["ficha"] = df_pendientes["id_usuario"].apply(lambda uid: usuarios_dict.get(uid, {}).get("ficha", ""))
            df_pendientes["fecha_realizacion"] = df_pendientes["fecha_realizacion"].apply(lambda f: f if f else "—")

            st.dataframe(df_pendientes[["nombre", "ficha", "estado", "fecha_realizacion", "porcentaje"]])

            # 🔽 Filtrar reprobados
            df_reprobados = df_pendientes[df_pendientes["estado"] == "reprobado"]

            if not df_reprobados.empty:
                st.subheader("📉 Usuarios Reprobados")
                st.dataframe(df_reprobados[["nombre", "ficha", "fecha_realizacion", "porcentaje"]])

                if st.button("📁 Exportar reprobados a Excel"):
                    # Crear Excel con encabezado del curso
                    titulo = f"Usuarios Reprobados - Curso: {curso_seleccionado}"
                    df_export = df_reprobados[["nombre", "ficha", "fecha_realizacion", "porcentaje"]]
                    df_export.to_excel("usuarios_reprobados.xlsx", index=False, sheet_name="Reprobados")

                    # Descargar
                    with open("usuarios_reprobados.xlsx", "rb") as f:
                        st.download_button(
                            label="Descargar Excel de Reprobados",
                            data=f,
                            file_name=f"reprobados_{curso_seleccionado}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("✅ No hay usuarios reprobados en este curso.")
        else:
            st.info("✅ Todos los usuarios han aprobado este curso.")
