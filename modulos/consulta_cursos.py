import streamlit as st
import pandas as pd
from datetime import datetime, date
from db.conexion import get_connection
from utils.helpers import calcular_vencimiento

supabase = get_connection()

def mostrar():
    # Encabezado con logos
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)

    st.header("Consulta de Cursos por Ficha")

    usuario_actual = st.session_state.get("usuario", {})
    ficha_actual = usuario_actual.get("ficha")
    rol_actual = usuario_actual.get("rol")

    if rol_actual == "administrador":
        ficha_consulta = st.text_input("Ingrese el número de ficha a consultar:")
    else:
        ficha_consulta = ficha_actual
        st.info(f"🔒 Consultando cursos para tu ficha: **{ficha_consulta}**")

    if ficha_consulta:
        usuario_resp = supabase.table("usuarios").select("id_usuario, nombre").eq("ficha", ficha_consulta).execute()
        if usuario_resp.data:
            usuario = usuario_resp.data[0]
            id_usuario = usuario["id_usuario"]
            nombre = usuario["nombre"]
            st.subheader(f"Cursos del usuario: {nombre}")

            promedio_resp = supabase.table("estado_cursos").select("porcentaje, estado").eq("id_usuario", id_usuario).execute()
            porcentajes = [r["porcentaje"] for r in promedio_resp.data if r["estado"] in ["realizado", "aprobado", "reprobado"]]
            if porcentajes:
                promedio = sum(porcentajes) / len(porcentajes)
                st.metric("📊 Promedio de cursos realizados", f"{promedio:.2f}%")
            else:
                st.info("Este usuario aún no tiene cursos con porcentaje registrado.")

            cursos_resp = supabase.table("estado_cursos").select("id_curso, fecha_realizacion, estado, porcentaje").eq("id_usuario", id_usuario).execute()
            cursos_data = cursos_resp.data

            if cursos_data:
                df = pd.DataFrame(cursos_data)
                curso_info = supabase.table("cursos").select("id_curso, nombre, frecuencia, modulo").execute().data
                curso_dict = {c["id_curso"]: c for c in curso_info}

                hoy = datetime.today()
                vencimientos = []
                estados_actualizados = []
                dias_restantes = []

                for i, row in df.iterrows():
                    curso = curso_dict.get(row["id_curso"], {})
                    df.at[i, "nombre"] = curso.get("nombre", "Desconocido")
                    df.at[i, "frecuencia"] = curso.get("frecuencia", "N/A")
                    df.at[i, "modulo"] = curso.get("modulo", "N/A")

                    fecha_raw = row.get("fecha_realizacion")
                    if fecha_raw:
                        fecha_realizacion = datetime.strptime(fecha_raw, "%Y-%m-%d")
                        vencimiento = calcular_vencimiento(fecha_realizacion, curso.get("frecuencia"))
                    else:
                        fecha_realizacion = None
                        vencimiento = None

                    if vencimiento:
                        vencimientos.append(vencimiento.date())
                        dias = (vencimiento - hoy).days
                        dias_restantes.append(dias)

                        if dias < 0:
                            estados_actualizados.append("pendiente")
                        elif dias <= 30:
                            estados_actualizados.append("por vencer")
                        else:
                            estados_actualizados.append(row["estado"])
                    else:
                        vencimientos.append("No vence")
                        dias_restantes.append("N/A")
                        estados_actualizados.append(row["estado"])

                df["fecha_vencimiento"] = pd.to_datetime([
                    v if isinstance(v, (datetime, date)) else pd.NaT for v in vencimientos
                ])
                df["días_restantes"] = dias_restantes
                df["estado_actualizado"] = estados_actualizados
                df = df.sort_values(by="fecha_vencimiento", ascending=True, na_position="last")
                df["fecha_vencimiento"] = [v if not pd.isna(v) else "No vence" for v in df["fecha_vencimiento"]]

                st.dataframe(df)

                if st.button("📁 Exportar a Excel"):
                    df.to_excel("reporte_cursos.xlsx", index=False)
                    with open("reporte_cursos.xlsx", "rb") as f:
                        st.download_button(
                            label="Descargar archivo Excel",
                            data=f,
                            file_name="reporte_cursos.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No se encontraron cursos registrados para este usuario.")
        else:
            st.warning("Ficha no encontrada. Verifique el número ingresado.")

    if rol_actual == "administrador":
        st.subheader("🔍 Usuarios con curso pendiente")

        cursos_resp = supabase.table("cursos").select("id_curso, nombre").execute()
        cursos_dict = {c["nombre"]: c["id_curso"] for c in cursos_resp.data}

        curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))

        if curso_seleccionado:
            id_curso = cursos_dict[curso_seleccionado]
            pendientes_resp = supabase.table("estado_cursos").select("id_usuario, estado, fecha_realizacion, porcentaje").eq("id_curso", id_curso).neq("estado", "aprobado").execute()
            pendientes_data = pendientes_resp.data
            if pendientes_data:
                usuarios_info = supabase.table("usuarios").select("id_usuario, nombre, ficha").execute().data
                usuarios_dict = {u["id_usuario"]: u for u in usuarios_info}

                df_pendientes = pd.DataFrame(pendientes_data)
                df_pendientes["nombre"] = df_pendientes["id_usuario"].apply(lambda uid: usuarios_dict.get(uid, {}).get("nombre", ""))
                df_pendientes["ficha"] = df_pendientes["id_usuario"].apply(lambda uid: usuarios_dict.get(uid, {}).get("ficha", ""))

                # Formatear fecha_realizacion solo si existe
                df_pendientes["fecha_realizacion"] = df_pendientes["fecha_realizacion"].apply(
                    lambda f: f if f else "—"
                )
                st.dataframe(df_pendientes[["nombre", "ficha", "estado", "fecha_realizacion", "porcentaje"]])

            else:
                st.info("✅ Todos los usuarios han aprobado este curso.")
