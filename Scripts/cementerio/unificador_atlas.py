import os
import json
import pandas as pd
from PIL import Image

# --- CONFIGURACIÓN ---
RUTA_FOTOS = 'fotos'
ARCHIVO_ZONAS = 'scripts/zonas.csv' 
ARCHIVO_JSON = 'puntos_mapa.json'

def obtener_estrellas(ruta):
    try:
        with Image.open(ruta) as img:
            exif = img.getexif()
            # ID 0x4746 es el estándar de Rating (estrellas) en Windows/Adobe
            rating = exif.get(0x4746, 0)
            return int(rating)
    except:
        return 0

def generar_atlas():
    # 1. Cargar el diccionario de coordenadas
    try:
        df_zonas = pd.read_csv(ARCHIVO_ZONAS)
        # Limpiamos espacios por si acaso
        df_zonas['zona'] = df_zonas['zona'].str.strip().str.lower()
        coords = df_zonas.set_index('zona').to_dict('index')
        print(f"✅ CSV cargado con {len(coords)} zonas identificadas.")
    except Exception as e:
        print(f"⚠️ Error cargando zonas.csv: {e}")
        coords = {}

    lista_puntos = []

    # 2. Escaneo de carpetas
    for raiz, carpetas, archivos in os.walk(RUTA_FOTOS):
        for nombre in archivos:
            if nombre.lower().endswith(('.webp', '.jpg', '.jpeg', '.png')):
                ruta_completa = os.path.join(raiz, nombre).replace("\\", "/")
                partes = ruta_completa.split('/')
                
                # Lógica de Prefijos y Zonas
                capa = "Etapa Nómada"
                zona_original = "general"
                
                # Buscamos la carpeta contenedora
                for p in reversed(partes[:-1]):
                    p_low = p.lower()
                    if p_low not in ['fotos', 'seleccion']:
                        zona_original = p_low
                        if p_low.startswith('pub_'):
                            capa = "Publicaciones & Prensa"
                        elif p_low.startswith('nomad_'):
                            capa = "Etapa Nómada"
                        break
                
                # Limpiamos el nombre para buscar en el CSV
                zona_busqueda = zona_original.replace('pub_', '').replace('nomad_', '').strip()
                
                # Asignar coordenadas
                c = coords.get(zona_busqueda, {"lat": -20.0, "lon": -60.0})
                
                # Leer estrellas (Rating)
                estrellas = obtener_estrellas(ruta_completa)

                lista_puntos.append({
                    "id": nombre,
                    "zona": zona_busqueda,
                    "capa": capa,
                    "lat": c['lat'],
                    "lon": c['lon'],
                    "thumb": f"./{ruta_completa}",
                    "estrellas": estrellas,
                    "relato": "Archivo SUR DAO" # Espacio para el texto de Haroldo
                })

    # 3. Guardar JSON
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(lista_puntos, f, indent=4, ensure_ascii=False)
    
    print(f"🚀 ATLAS ACTUALIZADO: {len(lista_puntos)} fotos listas.")

if __name__ == "__main__":
    generar_atlas()