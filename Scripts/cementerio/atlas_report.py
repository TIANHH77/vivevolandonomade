import sqlite3
import os

# Ruta de atlas.db
ruta_db = r"F:\RECUPERADAS\atlas.db"

# Conexión
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS fotos_altas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    hash TEXT UNIQUE,
    fecha TEXT,
    gps_lat REAL,
    gps_lon REAL,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS clips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    hash TEXT UNIQUE,
    formato TEXT,
    proyecto TEXT,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS selecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    hash TEXT UNIQUE,
    galeria TEXT,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS otros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    hash TEXT UNIQUE,
    descripcion TEXT,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

conn.commit()

# Mostrar ubicación
print("Ubicación de atlas.db:", os.path.abspath(ruta_db))

# Listar tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("\n--- Conteo por tabla ---")
for (tabla,) in tablas:
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    cantidad = cursor.fetchone()[0]
    print(f"{tabla}: {cantidad} registros")

print("\n--- Estadísticas GPS ---")
cursor.execute("SELECT COUNT(*) FROM fotos_altas WHERE gps_lat IS NOT NULL AND gps_lon IS NOT NULL")
con_gps = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM fotos_altas WHERE gps_lat IS NULL OR gps_lon IS NULL")
sin_gps = cursor.fetchone()[0]

print(f"Fotos con GPS: {con_gps}")
print(f"Fotos sin GPS: {sin_gps}")

conn.close()
