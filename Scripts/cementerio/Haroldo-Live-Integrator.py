import os
import json
import sqlite3
import pandas as pd
from PIL import Image, ImageFile

# --- CONFIGURACIÓN ---
ImageFile.LOAD_TRUNCATED_IMAGES = True
RUTA_MAESTRA = r"F:\haroldohorta_selecciones"
RUTA_DESTINO_WEB = r"F:\fotos"
ZONAS_CSV = r"F:\Scripts\zonas.csv"
DB_PATH = r"F:\haroldo_archivo.db"

def get_full_atlas():
    atlas = {}
    try:
        df_zonas = pd.read_csv(ZONAS_CSV)
        for _, row in df_zonas.iterrows():
            atlas[str(row['zona']).lower().strip()] = [row['gps_lat'], row['gps_lon']]
        print(f"📖 CSV cargado: {len(atlas)} zonas.")
    except:
        print("⚠️ El CSV está vacío o no existe. Usando backup manual.")
        atlas = {"nicaragua": [12.1364, -86.2514], "junin": [-34.5931, -60.9464]}
    return atlas

def procesar_mambo_reloaded():
    atlas_ref = get_full_atlas()
    # Ordenar por longitud de nombre: los más largos (específicos) primero
    zonas_ordenadas = sorted(atlas_ref.keys(), key=len, reverse=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"🚀 Mambo v25.1: Recuperando el mapa...")

    for root, dirs, files in os.walk(RUTA_MAESTRA):
        r_low = root.lower().replace('í','i').replace('á','a').replace('ó','o').replace('é','e').replace('ú','u')
        
        coords = None
        # BUSQUEDA INTELIGENTE: Si encuentra una zona específica, ignora la general
        for lugar in zonas_ordenadas:
            if lugar in r_low:
                coords = atlas_ref[lugar]
                # Si el lugar NO es solo un país, rompemos el bucle para quedarnos con el más específico
                if lugar not in ["chile", "argentina", "brasil", "bolivia", "peru", "alemania"]:
                    break

        if not coords: continue

        for file in files:
            if file.startswith('.') or 'DS_Store' in file: continue
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.nef', '.tif')):
                f_low = file.lower()
                capa = "General"
                
                if any(x in r_low or x in f_low for x in ["pub_", "libro", "litio", "suecia", "europa"]):
                    capa = "Editorial"
                elif any(x in r_low or x in f_low for x in ["nicaragua", "peru", "fordlandia", "antartica", "lota"]):
                    capa = "Corresponsal"
                elif any(x in r_low or x in f_low for x in ["junin", "vuelo", "buckeye"]):
                    capa = "Libre Vuelo"

                rel_path = os.path.relpath(root, RUTA_MAESTRA).replace("\\", "/")
                cursor.execute('''
                    INSERT OR REPLACE INTO fotos (filename, ruta_relativa, lat, lon, capa, titulo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (file, rel_path, coords[0], coords[1], capa, f"[{capa}] {file}"))

    conn.commit()

    # Generar JSON para el mapa
    cursor.execute("SELECT filename, ruta_relativa, lat, lon, capa, titulo FROM fotos")
    rows = cursor.fetchall()
    galeria_mapa = []
    for r in rows:
        thumb_name = os.path.splitext(r[0])[0] + ".webp"
        galeria_mapa.append({
            "id": r[0], "capa": r[4], "lat": r[2], "lon": r[3],
            "thumb": f"./fotos/{r[1]}/{thumb_name}".replace("//", "/"),
            "titulo": r[5]
        })
    
    with open(r'F:\puntos_mapa.json', 'w', encoding='utf-8') as f:
        json.dump(galeria_mapa, f, indent=4, ensure_ascii=False)
    
    conn.close()
    print(f"✅ Mapa reconstruido con {len(galeria_mapa)} puntos.")

if __name__ == "__main__":
    procesar_mambo_reloaded()
