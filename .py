import sqlite3
import pandas as pd
import os

# --- RUTAS (Asegúrate de que sean las correctas en tu sistema) ---
DB_PATH = r"C:\PROYECTOS\Atlas\vivevolandonomade\data\haroldo_indice.db"
CSV_REALES = r"C:\PROYECTOS\Atlas\HaroldoHorta\fotos_reales.csv"

def unificar_fuentes():
    if not os.path.exists(CSV_REALES):
        print(f"❌ Error: No se encuentra {CSV_REALES}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("📥 Cargando datos de Legado desde el CSV...")
    
    try:
        # 1. Leer el CSV de fotos reales (el universo de 5.8k de Legado)
        df_reales = pd.read_csv(CSV_REALES)
        
        # Renombramos columnas para que tengan un estándar limpio
        df_reales = df_reales.rename(columns={
            'id': 'hash_id',
            'ruta': 'ruta_absoluta',
            'fecha': 'fecha_captura'
        })

        # 2. Inyectar en la base de datos en una tabla nueva llamada 'legado'
        df_reales.to_sql('legado', conn, if_exists='replace', index=False)
        print("✅ Tabla 'legado' creada exitosamente.")

        # 3. Crear la VISTA MAESTRA (El puente definitivo)
        # Esta vista permite buscar en AMBAS tablas al mismo tiempo con un solo comando
        print("🌉 Construyendo la Vista Maestra de Originales...")
        cursor.execute("DROP VIEW IF EXISTS vista_maestra_originales")
        
        cursor.execute('''
            CREATE VIEW vista_maestra_originales AS
            SELECT 
                Nombre as nombre_archivo, 
                RutaFull as ruta_maestra, 
                'LIVE' as fuente_origen 
            FROM inventario
            UNION ALL
            SELECT 
                -- Extraemos solo el nombre del archivo de la ruta completa de Legado
                REPLACE(ruta_absoluta, RTRIM(ruta_absoluta, REPLACE(ruta_absoluta, '\\', '')), '') as nombre_archivo,
                ruta_absoluta as ruta_maestra, 
                'LEGADO' as fuente_origen 
            FROM legado
        ''')
        
        conn.commit()

        # --- REPORTE DE INTEGRACIÓN ---
        count_live = cursor.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]
        count_legado = cursor.execute("SELECT COUNT(*) FROM legado").fetchone()[0]
        
        print("\n" + "═"*45)
        print(f"🚀 INTEGRACIÓN COMPLETADA CON ÉXITO")
        print(f"📦 Registros en LIVE (OneDrive): {count_live}")
        print(f"📦 Registros en LEGADO (Discos D/F): {count_legado}")
        print(f"💎 Total de originales indexados: {count_live + count_legado}")
        print("═"*45)
        print("Ahora puedes usar la vista 'vista_maestra_originales' para tus auditorías.")

    except Exception as e:
        print(f"❌ Error durante la unificación: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    unificar_fuentes()