import json
import os

# --- CONFIGURACIÓN ---
ARCHIVO_ENTRADA = "auditoria_gps.json"
ARCHIVO_SALIDA = "puntos_nuevos_auto.json"

# Prefijo para la web (ajusta esto según dónde estén tus fotos en el servidor)
# Si en tu PC es E:/para_web/foto.jpg, en la web será: fotos/foto.jpg
PREFIJO_WEB = "fotos/" 

print(f"🔄 Convirtiendo {ARCHIVO_ENTRADA}...")

try:
    with open(ARCHIVO_ENTRADA, "r", encoding="utf-8") as f:
        datos = json.load(f)

    puntos_mapa = []
    
    for item in datos:
        if item.get("tiene_gps"):
            # Limpiamos el nombre del archivo
            nombre_archivo = os.path.basename(item["archivo"])
            
            # Creamos el objeto para el mapa
            nuevo_punto = {
                "id": nombre_archivo.split('.')[0], # Usamos el nombre sin extensión como ID
                "lat": item["lat"],
                "lon": item["lon"],
                "zona": "Automático",  # Puedes editar esto luego en el JSON
                "capa": "Aéreo",       # Asumimos que si tiene GPS, es dron/aérea
                "titulo": nombre_archivo,
                "thumb": PREFIJO_WEB + nombre_archivo, # Ruta relativa para la web
                "full": PREFIJO_WEB + nombre_archivo,
                "rating": 3 # Rating por defecto
            }
            puntos_mapa.append(nuevo_punto)

    # Guardar
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        json.dump(puntos_mapa, f, indent=2, ensure_ascii=False)

    print(f"✅ ¡Listo! Se crearon {len(puntos_mapa)} puntos en '{ARCHIVO_SALIDA}'")
    print("👉 Ahora copia el contenido de este archivo dentro de tu 'data/puntos_mapa.json'")

except FileNotFoundError:
    print("❌ Error: No encuentro el archivo 'auditoria_gps.json'.")