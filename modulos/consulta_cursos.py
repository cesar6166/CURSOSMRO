import streamlit as st
import pandas as pd
from datetime import datetime, date
from db.conexion import get_connection
from utils.helpers import calcular_vencimiento
def mostrar():
    conn = get_connection()
    cursor = conn.cursor()

    # Encabezado con logos
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("img/GREENBRIERLOGO.png", width=200)
    with col2:
        st.image("img/LOGO.jpeg", width=200)

    st.header("Consulta de Cursos por Ficha")

    # Obtener datos del usuario autenticado
    usuario_actual = st.session_state.get("usuario", {})
    ficha_actual = usuario_actual.get("ficha")
    rol_actual = usuario_actual.get("rol")

    # Si es administrador, puede ingresar cualquier ficha
    if rol_actual == "administrador":
        ficha_consulta = st.text_input("Ingrese el número de ficha a consultar:")
    else:
        ficha_consulta = ficha_actual
        st.info(f"🔒 Consultando cursos para tu ficha: **{ficha_consulta}**")

    if ficha_consulta:
        cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE ficha = ?", (ficha_consulta,))
        usuario = cursor.fetchone()

        if usuario:
            id_usuario, nombre = usuario
            st.subheader(f"Cursos del usuario: {nombre}")

            # Calcular promedio de porcentaje
            cursor.execute("""
                SELECT AVG(porcentaje)
                FROM estado_cursos
                WHERE id_usuario = ? AND estado IN ('realizado', 'aprobado', 'reprobado')
            """, (id_usuario,))
            promedio = cursor.fetchone()[0]

            if promedio is not None:
                st.metric("📊 Promedio de cursos realizados", f"{promedio:.2f}%")
            else:
                st.info("Este usuario aún no tiene cursos con porcentaje registrado.")

            query = """
            SELECT c.nombre, c.frecuencia, c.modalidad, e.fecha_realizacion, e.estado, e.porcentaje
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

    # Sección adicional solo para administradores
    if rol_actual == "administrador":
        st.subheader("🔍 Usuarios con curso pendiente")

        cursos_disponibles = cursor.execute("SELECT id_curso, nombre FROM cursos").fetchall()
        cursos_dict = {c[1]: c[0] for c in cursos_disponibles}

        curso_seleccionado = st.selectbox("Selecciona un curso:", list(cursos_dict.keys()))

        if curso_seleccionado:
            id_curso = cursos_dict[curso_seleccionado]

            query_pendientes = """
            SELECT u.nombre, u.ficha, e.estado, e.fecha_realizacion, e.porcentaje
            FROM estado_cursos e
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.id_curso = ? AND e.estado != 'aprobado'
            """
            df_pendientes = pd.read_sql_query(query_pendientes, conn, params=(id_curso,))

            if not df_pendientes.empty:
                st.dataframe(df_pendientes)
            else:
                st.info("✅ Todos los usuarios han aprobado este curso.")

