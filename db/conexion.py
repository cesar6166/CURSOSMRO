import sqlite3

##obtenemos la conexion a la base de datos
def get_connection():
    conn = sqlite3.connect("Cursos.db", check_same_thread=False)
    return conn

##creamos las tablas si no existen
def crear_tablas(conn):
    cursor = conn.cursor()
    # Crear tablas si no existen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ficha TEXT NOT NULL UNIQUE,
        rol TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cursos (
        id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        frecuencia TEXT NOT NULL,
        modulo TEXT DEFAULT 'pendiente'
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estado_cursos (
        id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_curso INTEGER NOT NULL,
        fecha_realizacion TEXT NOT NULL,
        estado TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
    )
    ''')


    conn.commit()