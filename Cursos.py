import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd

# ✅ Configuración de la página
st.set_page_config(
    page_title="Gestión de Cursos",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 📦 Conexión a Supabase
from db.conexion import get_connection
supabase = get_connection()

# 📄 Importamos las páginas
import modulos.alta_usuario as alta_usuarios
import modulos.alta_cursos as alta_cursos
import modulos.asignar_curso as asignar_curso
import modulos.consulta_cursos as consulta_cursos
import modulos.baja_curso as baja_curso
import modulos.baja_usuarios as baja_usuario
import modulos.Bienvenida as bienvenida_usuario
from modulos.usuarios_pendientes import mostrar_usuarios_pendientes
from modulos.revisar_solicitudes import mostrar_solicitudes


# 🔐 Función de autenticación
def autenticar_usuario():
    st.title("🔐 Inicio de Sesión")
    ficha = st.text_input("Ingrese su número de ficha:")
    if st.button("Ingresar"):
        response = supabase.table("usuarios").select("nombre, rol").eq("ficha", ficha).execute()
        if response.data:
            nombre = response.data[0]["nombre"]
            rol = response.data[0]["rol"]
            st.session_state["usuario"] = {"nombre": nombre, "ficha": ficha, "rol": rol}
            st.success(f"Bienvenido, {nombre} ({rol})")
            st.rerun()
        else:
            st.error("Ficha no encontrada.")

# 🔄 Verificar si ya hay sesión iniciada
if "usuario" not in st.session_state:
    autenticar_usuario()
    st.stop()

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
        "Dar de Baja a un Usuario",
        "Usuarios pendientes",
        "Revisar Solicitudes"

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
elif menu == "Usuarios pendientes":
    mostrar_usuarios_pendientes()
elif menu == "Revisar Solicitudes":
    mostrar_solicitudes()


# 🔓 Botón para cerrar sesión
if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()
