import streamlit as st
import pandas as pd
from datetime import datetime, date
from db.conexion import get_connection
from utils.helpers import calcular_vencimiento

def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    st.header("Consulta de Cursos por Ficha")
    ficha_ingresada = st.text_input("Ingrese su número de ficha:")

    # Obtener datos del usuario autenticado
    usuario_actual = st.session_state.get("usuario", {})
    ficha_actual = usuario_actual.get("ficha")
    rol_actual = usuario_actual.get("rol")

    # Validar acceso
    if ficha_ingresada:
        if rol_actual != "administrador" and ficha_ingresada != ficha_actual:
            st.error("⚠️ Solo puedes consultar tu propia ficha.")
            return

        cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE ficha = ?", (ficha_ingresada,))
        usuario = cursor.fetchone()

        if usuario:
            id_usuario, nombre = usuario
            st.subheader(f"Cursos del usuario: {nombre}")

            query = """
            SELECT c.nombre, c.frecuencia, c.modalidad, e.fecha_realizacion, e.estado
            FROM estado_cursos e
            JOIN cursos c ON e.id_curso = c.id_curso
            WHERE e.id_usuario = ?
            """
            df = pd.read_sql_query(query, conn, params=(id_usuario,))

            if not df.empty:
                hoy = datetime.today()
                vencimientos = []
                estados_actualizados = []
                dias_restantes = []

                for _, row in df.iterrows():
                    fecha_realizacion = datetime.strptime(row['fecha_realizacion'], "%Y-%m-%d")
                    vencimiento = calcular_vencimiento(fecha_realizacion, row['frecuencia'])

                    if vencimiento:
                        vencimientos.append(vencimiento.date())
                        dias = (vencimiento - hoy).days
                        dias_restantes.append(dias)

                        if dias < 0:
                            estados_actualizados.append("pendiente")
                        elif dias <= 30:
                            estados_actualizados.append("por vencer")
                        else:
                            estados_actualizados.append(row['estado'])
                    else:
                        vencimientos.append("No vence")
                        dias_restantes.append("N/A")
                        estados_actualizados.append(row['estado'])

                df['fecha_vencimiento'] = pd.to_datetime([
                    v if isinstance(v, (datetime, date)) else pd.NaT for v in vencimientos
                ])
                df['días_restantes'] = dias_restantes
                df['estado_actualizado'] = estados_actualizados

                df = df.sort_values(by='fecha_vencimiento', ascending=True, na_position='last')
                df['fecha_vencimiento'] = [v if not pd.isna(v) else "No vence" for v in df['fecha_vencimiento']]

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
