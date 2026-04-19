import os
from PIL import Image
from PIL.ExifTags import TAGS
import pandas as pd

# --- RUTA DE TUS FOTOS WEB ---
DIR_FOTOS_WEB = r"C:\PROYECTOS\Atlas\vivevolandonomade\fotos"

def analizar_metadatos_existentes():
    print("🔍 Escaneando ADN de los archivos web...")
    reporte_meta = []

    for root, dirs, files in os.walk(DIR_FOTOS_WEB):
        for f in files:
            if f.lower().endswith(('.webp', '.jpg', '.jpeg')):
                ruta = os.path.join(root, f)
                info = {"archivo": f, "tiene_exif": False, "fecha_original": None, "camara": None}
                
                try:
                    img = Image.open(ruta)
                    exif = img._getexif()
                    if exif:
                        info["tiene_exif"] = True
                        for tag, value in exif.items():
                            tag_name = TAGS.get(tag, tag)
                            if tag_name == 'DateTimeOriginal':
                                info["fecha_original"] = value
                            if tag_name == 'Model':
                                info["camara"] = value
                except:
                    pass
                
                reporte_meta.append(info)

    df = pd.DataFrame(reporte_meta)
    
    # ESTADÍSTICAS TÁCTICAS
    con_fecha = df[df['fecha_original'].notnull()]
    
    print("\n" + "═"*40)
    print(f"📊 DIAGNÓSTICO DE METADATA")
    print(f"📸 Fotos analizadas: {len(df)}")
    print(f"🧬 Fotos con ADN (EXIF): {len(df[df['tiene_exif'] == True])}")
    print(f"📅 Fotos con Fecha Original: {len(con_fecha)}")
    print("═"*40)
    
    if len(con_fecha) > 0:
        print("💡 ¡Buenas noticias! Podemos intentar un cruce masivo por FECHA Y HORA.")
    else:
        print("⚠️ Los archivos web están limpios. La metadata fue borrada al exportar.")

if __name__ == "__main__":
    analizar_metadatos_existentes()