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

# 🧭 Menú lateral
usuario = st.session_state["usuario"]
rol = usuario["rol"]

st.sidebar.title("📚 Gestión de Cursos")
st.sidebar.markdown(f"""
**👤 Usuario:** {usuario['nombre']}  
**🆔 Ficha:** {usuario['ficha']}  
**🔐 Rol:** {rol}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navegación")

# 📋 Opciones agrupadas por categoría con descripciones
opciones_descripciones = {
    "🏠 Inicio": "Página principal con bienvenida.",
    "👤 Usuarios | Alta de Usuarios": "Registrar nuevos usuarios en el sistema.",
    "👤 Usuarios | Dar de Baja a un Usuario": "Eliminar usuarios existentes.",
    "📘 Cursos | Alta de Cursos": "Registrar nuevos cursos disponibles.",
    "📘 Cursos | Asignar Curso a Usuario": "Asignar cursos a usuarios registrados.",
    "📘 Cursos | Dar de Baja Curso a Usuario": "Eliminar asignaciones de cursos.",
    "📘 Cursos | Consulta de Cursos": "Ver cursos asignados y disponibles.",
    "🛠️ Administración | Usuarios pendientes": "Revisar usuarios que aún no han sido aprobados.",
    "🛠️ Administración | Revisar Solicitudes": "Ver y gestionar solicitudes de cursos."
}

# Filtrar opciones según el rol
if rol == "administrador":
    opciones = list(opciones_descripciones.keys())
else:
    opciones = ["🏠 Inicio", "📘 Cursos | Consulta de Cursos"]

# 🎯 Navegación principal
opcion_seleccionada = st.sidebar.radio("Selecciona una opción", opciones)

# ℹ️ Mostrar descripción dinámica
st.sidebar.caption(f"ℹ️ {opciones_descripciones.get(opcion_seleccionada, '')}")

# 🔓 Botón para cerrar sesión
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# 🧭 Mostrar módulo correspondiente
if opcion_seleccionada == "🏠 Inicio":
    bienvenida_usuario.mostrar_bienvenida(usuario["nombre"])
elif "Alta de Usuarios" in opcion_seleccionada:
    alta_usuarios.mostrar()
elif "Dar de Baja a un Usuario" in opcion_seleccionada:
    baja_usuario.mostrar()
elif "Alta de Cursos" in opcion_seleccionada:
    alta_cursos.mostrar()
elif "Asignar Curso a Usuario" in opcion_seleccionada:
    asignar_curso.mostrar()
elif "Dar de Baja Curso a Usuario" in opcion_seleccionada:
    baja_curso.mostrar()
elif "Consulta de Cursos" in opcion_seleccionada:
    consulta_cursos.mostrar()
elif "Usuarios pendientes" in opcion_seleccionada:
    mostrar_usuarios_pendientes()
elif "Revisar Solicitudes" in opcion_seleccionada:
    mostrar_solicitudes()
