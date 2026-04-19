import os
import sqlite3
import pandas as pd
import re
from PIL import Image
from PIL.ExifTags import TAGS

# --- RUTAS ---
BASE_ATLAS = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DIR_FOTOS_WEB = os.path.join(BASE_ATLAS, "fotos")
DB_PATH = os.path.join(BASE_ATLAS, "data", "haroldo_indice.db")

def obtener_fecha_exif(ruta_imagen):
    """Extrae la fecha de captura original de los metadatos de la imagen."""
    try:
        img = Image.open(ruta_imagen)
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':
                    return value # Formato "YYYY:MM:DD HH:MM:SS"
    except:
        pass
    return None

def rescatar_huerfanas():
    print("🕵️ Iniciando operación de rescate de huérfanas...")
    conn = sqlite3.connect(DB_PATH)
    
    # Cargamos el reporte de huérfanas del paso anterior
    reporte_previo = pd.read_csv(os.path.join(BASE_ATLAS, "reporte_trazabilidad_final.csv"))
    huerfanas = reporte_previo[reporte_previo['estado'] == 'HUÉRFANO']['archivo_web'].tolist()
    
    log_rescate = []

    for f_web in huerfanas:
        vuelto_a_vincular = False
        ruta_completa_web = ""
        
        # 1. Localizar el archivo físico en las carpetas
        for root, dirs, files in os.walk(DIR_FOTOS_WEB):
            if f_web in files:
                ruta_completa_web = os.path.join(root, f_web)
                break
        
        if not ruta_completa_web: continue

        # --- CAPA 1: BÚSQUEDA POR ID NUMÉRICO ---
        # Extraemos números del nombre (ej: 'vuelo_9824' -> '9824')
        numeros = re.findall(r'\d+', f_web)
        if numeros:
            # Probamos con el número más largo encontrado (suele ser el ID de cámara)
            id_candidato = max(numeros, key=len)
            if len(id_candidato) >= 3: # Ignoramos números muy cortos
                query = "SELECT nombre_archivo, ruta_maestra, fuente_origen FROM vista_maestra_originales WHERE nombre_archivo LIKE ?"
                res = conn.execute(query, (f'%{id_candidato}%',)).fetchone()
                if res:
                    log_rescate.append({"archivo_web": f_web, "master": res[0], "ruta": res[1], "metodo": "ID_NUMÉRICO"})
                    vuelto_a_vincular = True

        # --- CAPA 2: BÚSQUEDA POR METADATOS (Si la Capa 1 falló) ---
        if not vuelto_a_vincular:
            fecha_exif = obtener_fecha_exif(ruta_completa_web)
            if fecha_exif:
                # La fecha suele venir como 2024:10:15... la pasamos a 2024-10-15 para el CSV de Legado
                fecha_busqueda = fecha_exif.replace(":", "-").split(" ")[0]
                
                # Buscamos en la tabla de Legado que sí tiene columna de fecha
                query = "SELECT ruta_absoluta FROM legado WHERE fecha_captura LIKE ? LIMIT 1"
                res = conn.execute(query, (f'%{fecha_busqueda}%',)).fetchone()
                if res:
                    log_rescate.append({"archivo_web": f_web, "master": "Match por Fecha", "ruta": res[0], "metodo": "EXIF_FECHA"})
                    vuelto_a_vincular = True

    conn.close()

    # 📊 RESULTADOS DEL RESCATE
    if log_rescate:
        df_rescate = pd.DataFrame(log_rescate)
        df_rescate.to_csv(os.path.join(BASE_ATLAS, "reporte_rescate_exitoso.csv"), index=False)
        print(f"✅ ¡Rescate finalizado! Se recuperaron vínculos para {len(df_rescate)} fotos.")
        print("Revisa 'reporte_rescate_exitoso.csv' para ver los nuevos masters encontrados.")
    else:
        print("❌ No se pudieron vincular más fotos mediante IDs o EXIF. Puede que los WebP no tengan metadatos.")

if __name__ == "__main__":
    rescatar_huerfanas()