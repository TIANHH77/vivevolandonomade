import os
import sqlite3
from PIL import Image
from PIL.ExifTags import TAGS

# --- CONFIGURACIÓN ---
# La ruta del "Caos" en tu OneDrive
ruta_caos = r"C:\Users\santi\OneDrive - Bicicultura\Haroldo_Live"
# La ruta de tu base de datos maestra
ruta_db = r"F:\RECUPERADAS\atlas.db"

def buscar_modelo_camara(ruta_archivo):
    """Abre la foto y busca si fue tomada con una Nikon."""
    try:
        img = Image.open(ruta_archivo)
        exif = img._getexif()
        img.close() # Cerramos rápido
        
        if exif:
            for tag, value in exif.items():
                nombre_tag = TAGS.get(tag, tag)
                if nombre_tag == 'Model':
                    return str(value) # Retorna ej: "NIKON D7200"
    except:
        pass
    return None

def filtrar_nikon():
    if not os.path.exists(ruta_caos):
        print(f"ERROR: No encuentro la carpeta: {ruta_caos}")
        return

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # 1. Creamos la tabla VIP para los hallazgos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solo_nikon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruta TEXT,
        camara TEXT,
        carpeta_original TEXT
    )
    """)
    
    # Limpiamos por si habías corrido pruebas antes
    cursor.execute("DELETE FROM solo_nikon")
    
    print(f"--- 🕵️‍♀️ Iniciando búsqueda de NIKON en: {ruta_caos} ---")
    print("(Paciencia: esto lee foto por foto...)")
    
    contador_total = 0
    contador_nikon = 0
    archivos_validos = (".jpg", ".jpeg", ".png", ".nef", ".tif", ".tiff")

    # Usamos scandir que es más rápido
    with os.scandir(ruta_caos) as it:
        for entry in it:
            if entry.is_file() and entry.name.lower().endswith(archivos_validos):
                contador_total += 1
                
                # Leemos la huella digital
                modelo = buscar_modelo_camara(entry.path)
                
                # --- EL FILTRO DE ORO ---
                # Buscamos "D7200", pero también aceptamos si dice solo "NIKON"
                if modelo and ("NIKON" in modelo.upper() or "D7200" in modelo.upper()):
                    
                    carpeta_padre = os.path.basename(os.path.dirname(entry.path))
                    
                    cursor.execute("""
                        INSERT INTO solo_nikon (ruta, camara, carpeta_original) 
                        VALUES (?, ?, ?)
                    """, (entry.path, modelo, carpeta_padre))
                    
                    contador_nikon += 1
                    print(f"📸 ¡ENCONTRADA! ({contador_nikon}) {entry.name} -> {modelo}")

                if contador_total % 500 == 0:
                    print(f"   ...Escaneados {contador_total} archivos...")

    conn.commit()
    conn.close()
    
    print("\n" + "="*40)
    print(f"FIN DEL ESCANEO")
    print(f"Total revisados: {contador_total}")
    print(f"✅ TESOROS NIKON IDENTIFICADOS: {contador_nikon}")
    print("="*40)
    print("AHORA SÍ: Puedes ejecutar el script de rescate.")

if __name__ == "__main__":
    filtrar_nikon()