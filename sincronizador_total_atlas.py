import os
import json
import sqlite3
import pandas as pd
import random
import math

# --- CONFIGURACIÓN ---
BASE_PATH = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DIR_FOTOS = os.path.join(BASE_PATH, "fotos")
DB_PATH = os.path.join(BASE_PATH, "data", "haroldo_indice.db")
JSON_MAPA = os.path.join(BASE_PATH, "data", "puntos_mapa.json")
GPS_JSON = os.path.join(BASE_PATH, "data", "auditoria_gps.json")
CSV_ZONAS = os.path.join(BASE_PATH, "data", "zonas.csv")

def obtener_capa_final(folder_name, has_youtube=False):
    if has_youtube: return "video"
    folder = folder_name.lower()
    if folder.startswith("fly_"): return "fly"
    if folder.startswith("pub_"): return "pub"
    if folder.startswith("nomad_"): return "nomad"
    return "nomad"

def sincronizar_todo():
    print(f"🛰️  Iniciando Sincronización Maestra (Espiral Fermat + {DIR_FOTOS})...")
    
    if not os.path.exists(CSV_ZONAS):
        print(f"❌ Error: No se encuentra {CSV_ZONAS}")
        return

    # 1. CARGAR ZONAS Y CONTADORES
    df_zonas = pd.read_csv(CSV_ZONAS, encoding='latin1').drop_duplicates(subset=['zona'], keep='last')
    dict_zonas = df_zonas.set_index('zona').to_dict('index')
    contadores_espiral = {} 

    # 2. PRESERVAR VIDEOS MANUALES
    puntos_manuales = {}
    if os.path.exists(JSON_MAPA):
        with open(JSON_MAPA, 'r', encoding='utf-8') as f:
            try:
                data_vieja = json.load(f)
                puntos_manuales = {p['id']: p for p in data_vieja if 'youtube_id' in p}
            except: pass

    # 3. CARGAR GPS Y DB
    dict_gps = {}
    if os.path.exists(GPS_JSON):
        with open(GPS_JSON, 'r', encoding='utf-8') as f:
            try:
                gps_data = json.load(f)
                dict_gps = {item['archivo'].lower(): item for item in gps_data if item.get('tiene_gps')}
            except: pass

    conn = sqlite3.connect(DB_PATH)
    mapeo_dict = {}
    try:
        mapeo_dict = pd.read_sql_query("SELECT * FROM mapeo_web", conn).set_index('archivo_web').to_dict('index')
    except: pass

    nuevos_puntos = []

    # 4. ESCANEO DE CARPETAS
    for carpeta in os.listdir(DIR_FOTOS):
        ruta_carpeta = os.path.join(DIR_FOTOS, carpeta)
        if not os.path.isdir(ruta_carpeta): continue

        for archivo in os.listdir(ruta_carpeta):
            if archivo.lower().endswith(('.webp', '.jpg', '.jpeg', '.png')):
                
                # REPARACIÓN DE VARIABLES
                info_gps = dict_gps.get(archivo.lower())
                vínculo = mapeo_dict.get(archivo)
                zona_key = carpeta.lower().replace("fly_","").replace("nomad_","").replace("pub_","").strip("_ ").replace(" ", "_")
                
                # Rating de Estrellas (Bridge)
                sufijos_elite = ["ff", "zz", "xx", "ss", "dd", "best", "top"]
                rating = 5 if any(x in archivo.lower() for x in sufijos_elite) else 1
                
                # --- LIMPIEZA SÓLO PARA EL TÍTULO VISUAL ---
                titulo_limpio = archivo.split('.')[0]
                for s in sufijos_elite + ["ret", "MGD"]:
                    titulo_limpio = titulo_limpio.replace(s, "").replace(s.upper(), "")
                titulo_limpio = titulo_limpio.replace("_", " ").strip().capitalize()
                if not titulo_limpio: titulo_limpio = "Registro Fotográfico"

                # --- LÓGICA DE COORDENADAS (Espiral Fermat) ---
                lat, lon = 0, 0
                if info_gps:
                    lat, lon = info_gps['lat'], info_gps['lon']
                else:
                    target = dict_zonas.get(zona_key, {'lat': -33.448, 'lon': -70.669})
                    n = contadores_espiral.get(zona_key, 0)
                    phi = n * 137.508 
                    r = 0.003 * (n ** 0.5) # Aumentado a 0.003 para dar más aire entre las 1500 fotos
                    
                    lat = target['lat'] + (r * math.cos(math.radians(phi)))
                    lon = target['lon'] + (r * math.sin(math.radians(phi)))
                    contadores_espiral[zona_key] = n + 1

                # --- CONSTRUCCIÓN DEL PUNTO (ID, TÍTULO Y RUTA SEPARADOS) ---
                nuevos_puntos.append({
                    "id": f"{carpeta}_{archivo}".replace(".", "_"),
                    "lat": lat, "lon": lon,
                    "zona": zona_key,
                    "capa": obtener_capa_final(carpeta),
                    "titulo": titulo_limpio,
                    "thumb": f"fotos/{carpeta}/{archivo}", # <--- RUTA REAL AL ARCHIVO
                    "full": f"fotos/{carpeta}/{archivo}",  # <--- RUTA REAL AL ARCHIVO
                    "rating": rating,
                    "has_master": True if vínculo else False,
                    "descripcion": f"Registro en zona {zona_key.replace('_',' ').capitalize()}"
                })

    # 5. MERGE Y GUARDADO
    total_dict = {p['id']: p for p in nuevos_puntos}
    for pid, pdata in puntos_manuales.items():
        pdata['capa'] = 'video'
        total_dict[pid] = pdata

    with open(JSON_MAPA, 'w', encoding='utf-8') as f:
        json.dump(list(total_dict.values()), f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"\n✅ BINGO: {len(total_dict)} puntos registrados en el Atlas.")
    print(f"📂 Archivo generado en: {JSON_MAPA}")

if __name__ == "__main__":
    sincronizar_todo()