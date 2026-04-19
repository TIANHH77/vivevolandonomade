from PIL import Image
import os

# --- CONFIGURACIÓN ---
# La carpeta de Nicaragua en el disco E:
CARPETA_ENTRADA = r"E:\para_web\Nicaragua"
# Tu carpeta de destino en el disco F:
CARPETA_SALIDA = r"F:\fotos\pub_nicaragua"

# Crear la carpeta de salida si no existe
if not os.path.exists(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA)
    print(f"📁 Carpeta creada: {CARPETA_SALIDA}")

print("🚀 Iniciando conversión masiva a WebP...")

# Extensiones que vamos a buscar
extensiones_validas = ('.jpg', '.jpeg', '.tif', '.tiff', '.png')

contador = 0

for archivo in os.listdir(CARPETA_ENTRADA):
    if archivo.lower().endswith(extensiones_validas):
        ruta_full_entrada = os.path.join(CARPETA_ENTRADA, archivo)
        
        # El nombre de salida será el mismo pero con extensión .webp
        nombre_base = os.path.splitext(archivo)[0]
        ruta_full_salida = os.path.join(CARPETA_SALIDA, f"{nombre_base}.webp")

        try:
            img = Image.open(ruta_full_entrada)
            
            # Convertir a RGB (necesario para TIF o PNG con transparencia)
            if img.mode in ("RGBA", "P", "CMYK", "I;16"):
                img = img.convert("RGB")
            
            # Redimensionar a Full HD (proporcional)
            img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
            
            # Guardar como WebP (más ligero que JPG)
            img.save(ruta_full_salida, "WEBP", quality=80)
            
            print(f"✅ Procesado: {archivo} -> {nombre_base}.webp")
            contador += 1

        except Exception as e:
            print(f"❌ Error en {archivo}: {e}")

print(f"\n✨ ¡Misión cumplida! Se convirtieron {contador} fotos a WebP en {CARPETA_SALIDA}")