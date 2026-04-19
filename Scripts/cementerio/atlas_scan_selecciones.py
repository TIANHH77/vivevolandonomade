import os
import sqlite3
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# --- CONFIGURACIÓN ---
ruta_db = r"F:\RECUPERADAS\atlas.db"
# Esta es la ruta correcta según tus capturas:
ruta_base = r"F:\RECUPERADAS\Selecciones" 

print(f"--- Iniciando escaneo en: {ruta_base} ---")

conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Crear tabla Selecciones si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS selecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo TEXT NOT NULL,
    fecha TEXT,
    gps_lat REAL,
    gps_lon REAL,
    estado TEXT CHECK(estado IN ('curado','duplicado'))
)
""")
conn.commit()

def convertir_a_decimal(valor):
    try:
        grados = float(valor[0])
        minutos = float(valor[1])
        segundos = float(valor[2])
        return grados + (minutos / 60.0) + (segundos / 3600.0)
    except:
        return 0.0

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

contador = 0

for raiz, _, archivos in os.walk(ruta_base):
    for archivo in archivos:
        ruta = os.path.join(raiz, archivo)
        fecha, lat, lon = None, None, None

        if archivo.lower().endswith((".jpg", ".jpeg", ".png", ".nef", ".tif", ".tiff")):
            exif = extraer_exif(ruta)
            fecha = exif.get("DateTimeOriginal", None)
            lat, lon = extraer_gps(exif)

            cursor.execute("""
                INSERT INTO selecciones (archivo, fecha, gps_lat, gps_lon, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (ruta, fecha, lat, lon, "curado"))
            
            contador += 1
            if contador % 1000 == 0:
                print(f"Procesadas {contador} fotos...")

conn.commit()
conn.close()
print(f"=== ¡ÉXITO! Se cargaron {contador} fotos en atlas.db ===")