import sqlite3
import pandas as pd
import os

# --- RUTAS ---
BASE_ATLAS = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DB_PATH = os.path.join(BASE_ATLAS, "data", "haroldo_indice.db")
REPORTE_1 = os.path.join(BASE_ATLAS, "reporte_trazabilidad_final.csv")
REPORTE_2 = os.path.join(BASE_ATLAS, "reporte_rescate_exitoso.csv")

def fijar_mapeo():
    if not os.path.exists(DB_PATH):
        print("❌ No se encuentra la DB.")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Cargar los reportes de lo que logramos vincular
    df1 = pd.read_csv(REPORTE_1)
    df1 = df1[df1['estado'] == 'VINCULADO'][['archivo_web', 'nombre_original', 'ruta_master', 'fuente']]
    
    df2 = pd.read_csv(REPORTE_2)
    df2 = df2.rename(columns={'master': 'nombre_original', 'ruta': 'ruta_master', 'metodo': 'fuente'})

    # Unir ambos éxitos
    df_final = pd.concat([df1, df2], ignore_index=True)

    # 2. Guardar en la DB
    print(f"📥 Guardando {len(df_final)} vínculos verificados en la tabla 'mapeo_web'...")
    df_final.to_sql('mapeo_web', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    print("✅ ¡Mapeo blindado! Ahora la DB contiene la relación directa entre la Web y los Originales.")

if __name__ == "__main__":
    fijar_mapeo()