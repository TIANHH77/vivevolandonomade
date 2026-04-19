import os
import sqlite3
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

ruta_db = r"F:\RECUPERADAS\atlas.db"
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Crear tablas
cursor.execute("""
CREATE TABLE IF NOT EXISTS fotos_altas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
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
    origen TEXT,
    formato TEXT,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS otros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT CHECK(estado IN ('nuevo','duplicado'))
)
""")

conn.commit()

def convertir_a_decimal(valor):
    grados = valor[0][0] / valor[0][1]
    minutos = valor[1][0] / valor[1][1]
    segundos = valor[2][0] / valor[2][1]
    return grados + (minutos / 60.0) + (segundos / 3600.0)

def extraer_exif(ruta):
    try:
        imagen = Image.open(ruta)
        exif = imagen._getexif()
        if not exif:
            return {}
        datos = {}
        for tag, valor in exif.items():
            nombre = TAGS.get(tag, tag)
            datos[nombre] = valor
        return datos
    except:
        return {}

def extraer_gps(exif):
    if "GPSInfo" not in exif:
        return None, None
    gps_info = {}
    for key in exif["GPSInfo"].keys():
        nombre = GPSTAGS.get(key, key)
        gps_info[nombre] = exif["GPSInfo"][key]

    lat = lon = None
    if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
        lat = convertir_a_decimal(gps_info["GPSLatitude"])
        if gps_info["GPSLatitudeRef"] != "N":
            lat = -lat
    if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
        lon = convertir_a_decimal(gps_info["GPSLongitude"])
        if gps_info["GPSLongitudeRef"] != "E":
            lon = -lon
    return lat, lon

ruta_base = r"F:\RECUPERADAS"

for raiz, _, archivos in os.walk(ruta_base):
    for archivo in archivos:
        ruta = os.path.join(raiz, archivo)
        fecha, lat, lon = None, None, None   # ← corregido y con indentación correcta

        if archivo.lower().endswith((".jpg", ".jpeg", ".png", ".nef", ".tif", ".tiff")):
            exif = extraer_exif(ruta)
            fecha = exif.get("DateTimeOriginal", None)
            lat, lon = extraer_gps(exif)
            cursor.execute("""
                INSERT INTO fotos_altas (archivo, fecha, gps_lat, gps_lon, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (ruta, fecha, lat, lon, "nuevo"))

        elif archivo.lower().endswith((".mp4", ".mov", ".avi")):
            cursor.execute("""
                INSERT INTO clips (archivo, origen, formato, estado)
                VALUES (?, ?, ?, ?)
            """, (ruta, "RECUPERADAS", "video", "nuevo"))

        else:
            cursor.execute("""
                INSERT INTO otros (archivo, descripcion, estado)
                VALUES (?, ?, ?)
            """, (ruta, "recuperadas", "nuevo"))

carpetas_clips = {
    r"F:\INSTA 360 VIDEOS Y CLIPS": "Insta360",
    r"F:\Dron Avata•": "Avata"
}

for carpeta, origen in carpetas_clips.items():
    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            if archivo.lower().endswith((".mp4", ".mov", ".avi")):
                cursor.execute("""
                    INSERT INTO clips (archivo, origen, formato, estado)
                    VALUES (?, ?, ?, ?)
                """, (ruta, origen, "video", "nuevo"))

conn.commit()
conn.close()
print("Carga de RECUPERADAS e INSTA360/Avata completada en atlas.db")



