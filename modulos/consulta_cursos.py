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
                            if row["estado"] in ["aprobado", "realizado"]:
                                estado_nuevo = "reprobado"
                            else:
                                estado_nuevo = "pendiente"
                        elif dias <= 30:
                            estado_nuevo = "por vencer"
                        else:
                            estado_nuevo = row["estado"]
                    else:
                        vencimientos.append("No vence")
                        dias_restantes.append("N/A")
                        estado_nuevo = row["estado"]

                    if estado_nuevo == "aprobado":
                        porcentaje_nuevo = 100
                    elif estado_nuevo == "reprobado":
                        porcentaje_nuevo = 0
                    else:
                        porcentaje_nuevo = row["porcentaje"]

                    estados_actualizados.append(estado_nuevo)
                    df.at[i, "porcentaje"] = porcentaje_nuevo

                    if estado_nuevo != row["estado"] or porcentaje_nuevo != row["porcentaje"]:
                        try:
                            supabase.table("estado_cursos").update({
                                "estado": estado_nuevo,
                                "porcentaje": porcentaje_nuevo
                            }).eq("id_usuario", id_usuario).eq("id_curso", row["id_curso"]).execute()
                        except Exception as e:
                            st.error(f"Error al actualizar estado/porcentaje en Supabase: {e}")

                porcentajes_actualizados = df[df["estado"].isin(["realizado", "aprobado", "reprobado"])]["porcentaje"]
                if not porcentajes_actualizados.empty:
                    promedio_usuario = porcentajes_actualizados.mean()
                    st.metric("📊 Promedio de cursos realizados", f"{promedio_usuario:.2f}%")
                else:
                    st.info("Este usuario aún no tiene cursos con porcentaje registrado.")

                todos_resp = supabase.table("estado_cursos").select("id_usuario, porcentaje, estado").execute()
                todos = todos_resp.data
                registros_validos = [r for r in todos if r["estado"] in ["realizado", "aprobado", "reprobado"]]
                df_promedios = pd.DataFrame(registros_validos)
                df_promedios = df_promedios.groupby("id_usuario")["porcentaje"].mean().reset_index()
                df_promedios = df_promedios.sort_values(by="porcentaje", ascending=False).reset_index(drop=True)

                medallas = ["🥇 Oro", "🥈 Plata", "🥉 Bronce"]
                df_promedios["medalla"] = ""
                for i in range(min(3, len(df_promedios))):
                    df_promedios.at[i, "medalla"] = medallas[i]

                promedio_general = df_promedios["porcentaje"].mean()
                st.metric("📈 Promedio general de todos los usuarios", f"{promedio_general:.2f}%")

                posicion_usuario = df_promedios[df_promedios["id_usuario"] == id_usuario].index
                if not posicion_usuario.empty:
                    posicion = posicion_usuario[0] + 1
                    medalla = df_promedios.loc[posicion_usuario[0], "medalla"]
                    st.success(f"🏅 Tu posición en el ranking: #{posicion}")
                    if medalla:
                        st.info(f"🎖️ ¡Has ganado medalla: {medalla}!")
                else:
                    st.info("Este usuario no tiene cursos registrados para el ranking.")

                df["fecha_vencimiento"] = pd.to_datetime([
                    v if isinstance(v, (datetime, date)) else pd.NaT for v in vencimientos
                ])
                df["días_restantes"] = dias_restantes
                df["estado_actualizado"] = estados_actualizados
                df = df.sort_values(by="fecha_vencimiento", ascending=True, na_position="last")
                df["fecha_vencimiento"] = [v if not pd.isna(v) else "No vence" for v in df["fecha_vencimiento"]]

                st.dataframe(df)

                st.subheader("📉 Cursos Reprobados")
                df_reprobados = df[df["estado"] == "reprobado"]
                if not df_reprobados.empty:
                    for i, row in df_reprobados.iterrows():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                                **Curso:** {row['nombre']}  
                                **Módulo:** {row['modulo']}  
                                **Porcentaje:** {row['porcentaje']}%  
                                **Fecha:** {row['fecha_realizacion']}
                            """)
                        with col2:
                            boton_id = f"solicitar_{row['id_curso']}_{i}"
                            if st.button("Solicitar aprobación", key=boton_id):
                                solicitud_existente = supabase.table("solicitudes_aprobacion").select("id_solicitud").eq("id_usuario", id_usuario).eq("id_curso", row["id_curso"]).eq("estado_solicitud", "pendiente").execute()
                                if solicitud_existente.data:
                                    st.warning("Ya existe una solicitud pendiente para este curso.")
                                else:
                                    supabase.table("solicitudes_aprobacion").insert({
                                        "id_usuario": id_usuario,
                                        "id_curso": row["id_curso"],
                                        "estado_solicitud": "pendiente",
                                        "fecha_solicitud": date.today().isoformat()
                                    }).execute()
                                    st.success("Solicitud enviada correctamente.")

                    if st.button("📁 Exportar cursos reprobados a Excel"):
                        df_reprobados.to_excel("reprobados.xlsx", index=False)
                        with open("reprobados.xlsx", "rb") as f:
                            st.download_button(
                                label="Descargar cursos reprobados",
                                data=f,
                                file_name="reprobados.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.info("✅ No hay cursos reprobados para este usuario.")

                if st.button("📁 Exportar todos los cursos a Excel"):
                    df.to_excel("reporte_cursos.xlsx", index=False)
                    with open("reporte_cursos.xlsx", "rb") as f:
                        st.download_button(
                            label="Descargar todos los cursos",
                            data=f,
                            file_name="reporte_cursos.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No se encontraron cursos registrados para este usuario.")
        else:
            st.warning("Ficha no encontrada. Verifique el número ingresado.")

