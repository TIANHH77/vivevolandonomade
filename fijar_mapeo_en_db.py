import sqlite3
import pandas as pd
import os

# --- CONFIGURACIÓN DE RUTAS ---
BASE_ATLAS = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DB_PATH = os.path.join(BASE_ATLAS, "data", "haroldo_indice.db")

# Rutas de los reportes que generamos con los éxitos
REPORTE_FINAL = os.path.join(BASE_ATLAS, "reporte_trazabilidad_final.csv")
REPORTE_RESCATE = os.path.join(BASE_ATLAS, "reporte_rescate_exitoso.csv")

def fijar_mapeo():
    print("🧠 Iniciando el blindaje de datos en el Búnker...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encuentra la DB en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    vínculos_totales = []

    # 1. Procesar Reporte Final (Las primeras 47 que machearon por nombre)
    if os.path.exists(REPORTE_FINAL):
        df1 = pd.read_csv(REPORTE_FINAL)
        # Solo nos interesan las que dicen VINCULADO
        df1_vinculadas = df1[df1['estado'] == 'VINCULADO'][['archivo_web', 'nombre_original', 'ruta_master', 'fuente']]
        vínculos_totales.append(df1_vinculadas)
        print(f"✅ Cargadas {len(df1_vinculadas)} fotos del reporte de trazabilidad.")

    # 2. Procesar Reporte de Rescate (Las 19 que rescatamos por ID/Fecha)
    if os.path.exists(REPORTE_RESCATE):
        df2 = pd.read_csv(REPORTE_RESCATE)
        # Renombramos columnas para que coincidan con la tabla
        df2 = df2.rename(columns={'archivo_web': 'archivo_web', 'master': 'nombre_original', 'ruta': 'ruta_master', 'metodo': 'fuente'})
        vínculos_totales.append(df2)
        print(f"✅ Cargadas {len(df2)} fotos del reporte de rescate.")

    if not vínculos_totales:
        print("⚠️ No se encontraron archivos CSV con vínculos para procesar.")
        return

    # 3. Unificar y Guardar en la DB
    df_final = pd.concat(vínculos_totales, ignore_index=True)
    
    # Eliminamos duplicados por si acaso
    df_final = df_final.drop_duplicates(subset=['archivo_web'])

    print(f"📥 Guardando {len(df_final)} vínculos maestros en la tabla 'mapeo_web'...")
    df_final.to_sql('mapeo_web', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    
    print("\n" + "═"*45)
    print("💎 ¡PROCESO FINALIZADO!")
    print(f"La tabla 'mapeo_web' ha sido creada/actualizada.")
    print("Ahora puedes correr 'sincronizador_total_atlas.py'.")
    print("═"*45)

if __name__ == "__main__":
    fijar_mapeo()