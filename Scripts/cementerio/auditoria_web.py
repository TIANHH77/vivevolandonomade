from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import json
import os
import sys

# --- CONFIGURACIÓN ACTUALIZADA ---
# Usamos barras normales (/) para evitar problemas en Python
CARPETA_A_ESCANEAR = "E:/para_web/" 
ARCHIVO_SALIDA = "auditoria_gps.json"

def extraer_gps(ruta_foto):
    """Extrae coordenadas GPS de una foto con manejo de errores robusto"""
    try:
        img = Image.open(ruta_foto)
        exif = img._getexif()
        
        if not exif:
            return None
        
        gps_data = {}
        for tag, valor in exif.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag in valor:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[gps_tag_name] = valor[gps_tag]
        
        if not gps_data:
            return None
            
        # Convertir a decimal
        lat = gps_data.get('GPSLatitude')
        lon = gps_data.get('GPSLongitude')
        
        if lat and lon:
            # Función auxiliar para asegurar conversión a float
            def to_float(val):
                try:
                    return float(val)
                except:
                    # Si es una tupla (numerador, denominador)
                    if isinstance(val, tuple) or isinstance(val, list):
                        return float(val[0]) / float(val[1]) if val[1] != 0 else 0
                    # Si es IFDRational de PILLOW
                    if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                        return float(val.numerator) / float(val.denominator)
                    return 0.0

            lat_decimal = to_float(lat[0]) + to_float(lat[1])/60 + to_float(lat[2])/3600
            lon_decimal = to_float(lon[0]) + to_float(lon[1])/60 + to_float(lon[2])/3600
            
            # Ajustar hemisferios
            if gps_data.get('GPSLatitudeRef') == 'S':
                lat_decimal = -lat_decimal
            if gps_data.get('GPSLongitudeRef') == 'W':
                lon_decimal = -lon_decimal
                
            return {"lat": lat_decimal, "lon": lon_decimal}
    except Exception as e:
        # Si falla, simplemente retornamos None para seguir con la siguiente
        return None
    return None

# --- INICIO DEL ESCANEO ---
print(f"🚀 Iniciando auditoría en: {CARPETA_A_ESCANEAR}")
print("------------------------------------------------")
resultados = []
contador = 0
con_gps = 0

for root, dirs, files in os.walk(CARPETA_A_ESCANEAR):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif', '.webp', '.png')):
            ruta = os.path.join(root, file)
            contador += 1
            
            # Extraer data
            coords = extraer_gps(ruta)
            
            # Guardar resultado preliminar
            item = {
                "archivo": file,
                "ruta_relativa": os.path.relpath(ruta, CARPETA_A_ESCANEAR), # Guardamos ruta relativa para que sea más limpio
                "tiene_gps": False
            }

            if coords:
                item["lat"] = coords["lat"]
                item["lon"] = coords["lon"]
                item["tiene_gps"] = True
                con_gps += 1
            
            resultados.append(item)

            # Feedback visual cada 50 fotos (más rápido)
            if contador % 50 == 0:
                sys.stdout.write(f"\r📸 Procesadas: {contador} | ✅ Con GPS: {con_gps}")
                sys.stdout.flush()

# Guardar resultado final
print(f"\n\n💾 Guardando informe en {ARCHIVO_SALIDA}...")
with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("\n" + "="*50)
print(f"✅ FINALIZADO EL ESCANEO DE {CARPETA_A_ESCANEAR}")
print(f"📂 Total archivos analizados: {len(resultados)}")
print(f"📍 Con coordenadas GPS: {con_gps}")
print(f"❌ Sin coordenadas GPS: {len(resultados) - con_gps}")
if len(resultados) > 0:
    print(f"📊 Tasa de éxito: {(con_gps/len(resultados)*100):.1f}%")
else:
    print("⚠️ No se encontraron imágenes en la carpeta.")
print("="*50)