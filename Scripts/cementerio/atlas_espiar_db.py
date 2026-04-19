import sqlite3
import os

# --- PEGA AQUÍ LA RUTA DE TU BASE DE DATOS DEL DISCO DE 28TB ---
# Ejemplo: r"F:\Haroldo_Live\db\catalogo_viejo.db"
ruta_db_antigua = r"C:\Users\santi\OneDrive - Bicicultura\Haroldo_Live\db\haroldo_indice.db"

def espiar_db():
    ruta_limpia = ruta_db_antigua.replace('"', '') # Limpia comillas por si acaso
    
    if "PEGAR_TU_RUTA" in ruta_limpia or not os.path.exists(ruta_limpia):
        print(f"⚠️ ERROR: No encuentro el archivo en: {ruta_limpia}")
        print("Edita el script y pon la ruta correcta.")
        return

    conn = sqlite3.connect(ruta_limpia)
    cursor = conn.cursor()

    print(f"--- LEYENDO ESTRUCTURA DE: {os.path.basename(ruta_limpia)} ---")
    
    # 1. Ver Tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    for tabla in tablas:
        nombre = tabla[0]
        if nombre == "sqlite_sequence": continue
        
        print(f"\n📂 TABLA: '{nombre}'")
        
        # 2. Ver Columnas
        cursor.execute(f"PRAGMA table_info({nombre})")
        cols = cursor.fetchall()
        nombres_col = [c[1] for c in cols]
        print(f"   📝 Columnas: {nombres_col}")
        
        # 3. Ver cantidad de datos
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
            total = cursor.fetchone()[0]
            print(f"   🔢 Total registros: {total}")
        except:
            print("   (No se pudo contar)")

        # 4. Ver un ejemplo (para saber qué pinta tiene la data)
        try:
            cursor.execute(f"SELECT * FROM {nombre} LIMIT 1")
            ejemplo = cursor.fetchone()
            print(f"   👀 Ejemplo: {ejemplo}")
        except:
            pass

    conn.close()

if __name__ == "__main__":
    espiar_db()