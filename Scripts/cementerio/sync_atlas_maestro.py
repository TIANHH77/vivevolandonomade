import os
import pandas as pd
import sqlite3

# --- RUTAS ---
BASE_ATLAS = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DIR_FOTOS_WEB = os.path.join(BASE_ATLAS, "fotos")
DB_LIVE = os.path.join(BASE_ATLAS, "data", "haroldo_indice.db")

# Nuevos CSVs
CSV_REALES = "fotos_reales.csv"
CSV_LEGADO = "indice_fotos_export.csv"

def auditoria_total():
    print("🚀 Iniciando Auditoría de Trazabilidad...")
    
    # 1. Cargar bases de datos de originales
    conn = sqlite3.connect(DB_LIVE)
    df_live = pd.read_sql_query("SELECT Nombre, RutaFull FROM inventario", conn)
    conn.close()
    
    df_reales = pd.read_csv(CSV_REALES)
    df_legado = pd.read_csv(CSV_LEGADO)

    reporte = []

    # 2. Escanear fotos de la web (tu selección actual)
    for root, dirs, files in os.walk(DIR_FOTOS_WEB):
        for f in files:
            if f.lower().endswith(('.webp', '.jpg', '.jpeg')):
                # Nombre base para buscar coincidencias
                nombre_base = f.split('.')[0].lower()
                
                master_encontrado = "No identificado"
                fuente = "Ninguna"
                ruta_original = "N/A"

                # A. Buscar en Mundos Reales (CSV Legado)
                # Buscamos si el nombre del archivo está contenido en la ruta del CSV
                match_legado = df_reales[df_reales['ruta'].str.lower().str.contains(nombre_base)]
                if not match_legado.empty:
                    fuente = "LEGADO (Disco D/F)"
                    ruta_original = match_legado.iloc[0]['ruta']
                
                # B. Buscar en Mundo Live (DB 54k)
                else:
                    match_live = df_live[df_live['Nombre'].str.lower().str.contains(nombre_base)]
                    if not match_live.empty:
                        fuente = "LIVE (OneDrive/C)"
                        ruta_original = match_live.iloc[0]['RutaFull']

                reporte.append({
                    "archivo_web": f,
                    "fuente_original": fuente,
                    "ubicacion_master": ruta_original
                })

    # 3. Guardar el reporte de trazabilidad
    df_final = pd.DataFrame(reporte)
    df_final.to_csv("reporte_trazabilidad_atlas.csv", index=False)
    
    print("\n" + "═"*40)
    print(f"✅ AUDITORÍA FINALIZADA")
    print(f"📸 Fotos en la web analizadas: {len(df_final)}")
    print(f"🔍 Con master identificado: {len(df_final[df_final['fuente_original'] != 'Ninguna'])}")
    print("═"*40)
    print("Archivo generado: reporte_trazabilidad_atlas.csv")

if __name__ == "__main__":
    auditoria_total()