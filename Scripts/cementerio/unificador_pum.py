import sqlite3
import json
import pandas as pd
import os

# CONFIGURACIÓN RUTAS (Ajustadas para vivir en /scripts)
DB_PATH = r'F:\haroldo_archivo.db'
ZONA_CSV = r'F:\scripts\zonas.csv' # Asegúrate que el archivo se llame zonas.csv
OUTPUT_JSON = r'F:\puntos_mapa.json'

def unificador_pum_final():
    print("🚀 PUM v26.1: Sincronizando Búnker con el Atlas...")
    
    if not os.path.exists(ZONA_CSV):
        print(f"❌ No se encontró {ZONA_CSV}")
        return
    
    zonas_dict = pd.read_csv(ZONA_CSV).set_index('zona').to_dict('index')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT filename, ruta_relativa, lat, lon, capa, titulo FROM fotos")
    rows = cursor.fetchall()
    
    puntos = []
    for r in rows:
        filename, ruta, lat, lon, capa, titulo = r
        desc = "Archivo SUR DAO"
        for k, v in zonas_dict.items():
            if k.lower() in ruta.lower():
                desc = v.get('descripcion', desc)
                break
        
        puntos.append({
            "id": filename, "capa": capa, "lat": lat, "lon": lon,
            "thumb": f"./fotos/{ruta}/{os.path.splitext(filename)[0]}.webp",
            "titulo": titulo, "relato": desc
        })

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(puntos, f, indent=4, ensure_ascii=False)
    
    conn.close()
    print(f"✨ ¡PUM! {len(puntos)} puntos listos en la raíz.")

if __name__ == "__main__":
    unificador_pum_final()
