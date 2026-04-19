import sqlite3
import os
import json

# --- CONFIGURACIÓN ---
DB_PATH = r"F:\haroldo_archivo.db"
JSON_ACTUAL = r"F:\puntos_mapa.json"

def inicializar_db():
    print(f"🗄️ Creando base de datos en {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creamos la tabla maestra
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            ruta_relativa TEXT,
            lat REAL,
            lon REAL,
            capa TEXT,
            titulo TEXT,
            fecha_modificacion DATETIME,
            tags TEXT
        )
    ''')
    
    conn.commit()
    return conn

def migrar_json_a_db(conn):
    if not os.path.exists(JSON_ACTUAL):
        print("⚠️ No hay JSON previo para migrar.")
        return

    with open(JSON_ACTUAL, 'r', encoding='utf-8') as f:
        puntos = json.load(f)

    cursor = conn.cursor()
    print(f"🚚 Migrando {len(puntos)} puntos del JSON a la DB...")
    
    for p in puntos:
        # Extraemos la ruta relativa del thumb para guardarla limpia
        # thumb: "./fotos/chile/san_pedro/foto.webp" -> ruta_rel: "chile/san_pedro"
        ruta_limpia = "/".join(p['thumb'].split('/')[2:-1])
        
        cursor.execute('''
            INSERT OR REPLACE INTO fotos (filename, ruta_relativa, lat, lon, capa, titulo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (p['id'], ruta_limpia, p['lat'], p['lon'], p['capa'], p['titulo']))
    
    conn.commit()
    print("✅ Migración completada.")

if __name__ == "__main__":
    conexion = inicializar_db()
    migrar_json_a_db(conexion)
    conexion.close()
    print(f"\n🚀 ¡Base de datos lista! Ahora F:\ es una biblioteca inteligente.")