import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date

# ✅ Configuración de la página (debe ir primero)
st.set_page_config(
    page_title="Gestión de Cursos",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📦 Importamos la conexión a la base de datos
from db.conexion import get_connection, crear_tablas

# 📄 Importamos las páginas
import modulos.alta_usuario as alta_usuarios
import modulos.alta_cursos as alta_cursos
import modulos.asignar_curso as asignar_curso
import modulos.consulta_cursos as consulta_cursos
import modulos.baja_curso as baja_curso
import modulos.baja_usuarios as baja_usuario
import modulos.Bienvenida as bienvenida_usuario

# 🔐 Función de autenticación
def autenticar_usuario():
    st.title("🔐 Inicio de Sesión")
    ficha = st.text_input("Ingrese su número de ficha:")
    if st.button("Ingresar"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, rol FROM usuarios WHERE ficha = ?", (ficha,))
        resultado = cursor.fetchone()
        if resultado:
            nombre, rol = resultado
            st.session_state["usuario"] = {"nombre": nombre, "ficha": ficha, "rol": rol}
            st.success(f"Bienvenido, {nombre} ({rol})")
            st.rerun()
        else:
            st.error("Ficha no encontrada.")

# 🔄 Verificar si ya hay sesión iniciada
if "usuario" not in st.session_state:
    autenticar_usuario()
    st.stop()

# 🗃️ Inicializar base de datos
conn = get_connection()
crear_tablas(conn)

# 🧭 Menú lateral según rol
rol = st.session_state["usuario"]["rol"]
st.sidebar.title("Menú")

if rol == "administrador":
    menu = st.sidebar.selectbox("Selecciona una opción", [
        "Info",
        "Consulta de Cursos",
        "Alta de Usuarios",
        "Alta de Cursos",
        "Asignar Curso a Usuario",
        "Dar de Baja Curso a Usuario",
        "Dar de Baja a un Usuario"
        
    ])
else:
    menu = st.sidebar.selectbox("Selecciona una opción", [
        "Info",
        "Consulta de Cursos"
    ])

# 🔄 Navegación entre páginas
if menu == "Info":
    nombre = st.session_state["usuario"]["nombre"]
    bienvenida_usuario.mostrar_bienvenida(nombre)
elif menu == "Consulta de Cursos":
    consulta_cursos.mostrar()
elif menu == 'Alta de Usuarios':
    alta_usuarios.mostrar()
elif menu == 'Alta de Cursos':
    alta_cursos.mostrar()
elif menu == 'Asignar Curso a Usuario':
    asignar_curso.mostrar()
elif menu == "Dar de Baja Curso a Usuario":
    baja_curso.mostrar()
elif menu == "Dar de Baja a un Usuario":
    baja_usuario.mostrar()

# 🔓 Botón para cerrar sesión
if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
