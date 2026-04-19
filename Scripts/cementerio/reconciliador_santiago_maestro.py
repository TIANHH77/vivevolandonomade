import os
import sqlite3
import pandas as pd
import json

# --- CONFIGURACIÓN DE RUTAS ---
# Escaneo total de la raíz de Haroldo
UNIVERSO_HAROLDO = r"C:\PROYECTOS\Atlas\HaroldoHorta"
DB_PATH = r"C:\PROYECTOS\Atlas\vivevolandonomade\data\haroldo_indice.db"
# Ajustamos la ruta del GPS al lugar donde suele estar
GPS_JSON = r"C:\PROYECTOS\Atlas\vivevolandonomade\auditoria_gps.json" 

def reconciliacion_masiva():
    print(f"🚀 Iniciando el 'Radar Total' en: {UNIVERSO_HAROLDO}")
    
    if not os.path.exists(UNIVERSO_HAROLDO):
        print("❌ Error: No se encuentra la carpeta raíz.")
        return

    # 1. Cargar Base de Datos y GPS
    conn = sqlite3.connect(DB_PATH)
    dict_gps = {}
    if os.path.exists(GPS_JSON):
        try:
            with open(GPS_JSON, 'r', encoding='utf-8') as f:
                data_gps = json.load(f)
            dict_gps = {item['archivo'].lower(): item for item in data_gps if item.get('tiene_gps')}
            print("📍 JSON de GPS cargado correctamente.")
        except Exception as e:
            print(f"⚠️ Error al leer GPS_JSON: {e}")
    else:
        print("⚠️ Nota: No se encontró auditoria_gps.json, se omitirá el cruce de GPS.")

    # 2. Escaneo recursivo de archivos (esto busca en todas las subcarpetas)
    print("📂 Escaneando archivos en el disco (esto puede demorar)...")
    reporte = []
    
    # Extensiones de imagen que buscamos
    extensiones = ('.jpg', '.jpeg', '.webp', '.nef', '.tif', '.tiff')

    for root, dirs, files in os.walk(UNIVERSO_HAROLDO):
        for f in files:
            if f.lower().endswith(extensiones):
                nombre_lower = f.lower()
                
                # A. Buscar coincidencia en la Vista Maestra (60k)
                query = "SELECT fuente_origen, ruta_maestra FROM vista_maestra_originales WHERE LOWER(nombre_archivo) = ?"
                res_db = conn.execute(query, (nombre_lower,)).fetchone()
                
                # B. Verificar GPS
                info_gps = dict_gps.get(nombre_lower)
                
                if res_db:
                    reporte.append({
                        "archivo_nombre": f,
                        "fuente": res_db[0],
                        "ruta_maestra": res_db[1],
                        "gps": "SÍ" if info_gps else "NO",
                        "carpeta_donde_esta": root
                    })

    conn.close()

    # 3. Generar el Reporte Final
    if reporte:
        df = pd.DataFrame(reporte)
        # Eliminamos duplicados por si el mismo archivo está en dos carpetas
        df = df.drop_duplicates(subset=['archivo_nombre'])
        
        output = "reporte_universo_haroldo_final.csv"
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        print("\n" + "═"*45)
        print(f"✅ ¡BARRIDO COMPLETO FINALIZADO!")
        print(f"💎 Coincidencias encontradas: {len(df)}")
        print(f"📍 Con datos GPS: {len(df[df['gps'] == 'SÍ'])}")
        print(f"📄 Reporte generado: {output}")
        print("═"*45)
    else:
        print("❌ No se encontraron coincidencias en el escaneo masivo.")

if __name__ == "__main__":
    reconciliacion_masiva()