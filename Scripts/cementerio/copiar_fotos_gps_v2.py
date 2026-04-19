import json
import os
import shutil

# --- CONFIGURACIÓN ---
ARCHIVO_AUDITORIA = "auditoria_gps.json"
CARPETA_ORIGEN = "E:/para_web/"  # Carpeta base donde están las fotos
CARPETA_DESTINO = "F:/fotos/"     # Carpeta de destino del proyecto

print(f"🚀 Iniciando la cosecha inteligente...")
print("-" * 40)

if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)
    print(f"📁 Creada la carpeta: {CARPETA_DESTINO}")

try:
    with open(ARCHIVO_AUDITORIA, "r", encoding="utf-8") as f:
        datos = json.load(f)

    contador_copiados = 0
    contador_existentes = 0
    
    for foto in datos:
        # Solo procesar si tiene GPS
        if foto.get("tiene_gps"):
            # Reconstrucción de la ruta: carpeta base + ruta relativa del JSON
            ruta_relativa_limpia = foto["ruta_relativa"].replace("\\", "/") # Normalizar barras
            ruta_origen = os.path.join(CARPETA_ORIGEN, ruta_relativa_limpia)
            
            nombre_archivo = foto["archivo"]
            ruta_destino = os.path.join(CARPETA_DESTINO, nombre_archivo)

            # Verificar si ya existe en el destino
            if os.path.exists(ruta_destino):
                contador_existentes += 1
                continue

            try:
                # Verificar si el archivo de origen realmente existe
                if os.path.exists(ruta_origen):
                    shutil.copy2(ruta_origen, ruta_destino)
                    contador_copiados += 1
                    print(f"✅ Copiada [{contador_copiados}]: {nombre_archivo}")
                else:
                    print(f"⚠️  No se encontró en el origen: {ruta_origen}")
            except Exception as e:
                print(f"❌ Error al copiar {nombre_archivo}: {e}")

    print("\n" + "="*50)
    print(f"✨ RESUMEN DE LA MISIÓN:")
    print(f"📸 Fotos nuevas copiadas: {contador_copiados}")
    print(f"♻️  Fotos que ya existían: {contador_existentes}")
    print(f"📂 Ubicación: {CARPETA_DESTINO}")
    print("="*50)

except FileNotFoundError:
    print(f"❌ No se encontró el archivo {ARCHIVO_AUDITORIA} en la carpeta actual.")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")