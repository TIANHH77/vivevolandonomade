import os
import json
import shutil

# ================= CONFIGURACIÓN =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_FOTOS = os.path.join(BASE_DIR, "fotos")
ARCHIVO_SALIDA = os.path.join(BASE_DIR, "data", "puntos_mapa.json")

def limpiar_nombre(nombre):
    # 1. Todo a minúsculas
    nuevo = nombre.lower()
    # 2. Reemplazar espacios por guiones bajos
    nuevo = nuevo.replace(" ", "_")
    # 3. Quitar caracteres latinos problemáticos (tildes, ñ)
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"),
        ("Á", "a"), ("É", "e"), ("Í", "i"), ("Ó", "o"), ("Ú", "u"), ("Ñ", "n")
    )
    for a, b in reemplazos:
        nuevo = nuevo.replace(a, b)
    return nuevo

def normalizar_sistema_archivos():
    print("🚜 INICIANDO APLANADORA DE NOMBRES...")
    cambios = 0

    # CAMINAMOS DE ABAJO HACIA ARRIBA (bottomdown=False) 
    # para renombrar archivos antes que las carpetas que los contienen
    for root, dirs, files in os.walk(RUTA_FOTOS, topdown=False):
        
        # 1. RENOMBRAR ARCHIVOS
        for filename in files:
            nombre_viejo = os.path.join(root, filename)
            nombre_limpio = limpiar_nombre(filename)
            
            if filename != nombre_limpio:
                nombre_nuevo = os.path.join(root, nombre_limpio)
                try:
                    os.rename(nombre_viejo, nombre_nuevo)
                    print(f"   ✏️ Archivo: {filename} -> {nombre_limpio}")
                    cambios += 1
                except Exception as e:
                    print(f"   ⚠️ Error renombrando {filename}: {e}")

        # 2. RENOMBRAR CARPETAS
        for dirname in dirs:
            ruta_vieja = os.path.join(root, dirname)
            nombre_limpio = limpiar_nombre(dirname)
            
            if dirname != nombre_limpio:
                ruta_nueva = os.path.join(root, nombre_limpio)
                try:
                    os.rename(ruta_vieja, ruta_nueva)
                    print(f"   📁 Carpeta: {dirname} -> {nombre_limpio}")
                    cambios += 1
                except Exception as e:
                    print(f"   ⚠️ Error renombrando carpeta {dirname}: {e}")

    print(f"✨ ¡Listo! Se normalizaron {cambios} elementos.")
    
    # 3. EJECUTAR EL ESCANEO FINAL (Importamos el otro script)
    print("\n🔄 Actualizando base de datos JSON...")
    # Truco para llamar al otro script sin copiar código
    os.system(f"python {os.path.join(BASE_DIR, 'Scripts', 'unificar_atlas.py')}")

if __name__ == "__main__":
    confirm = input("⚠️ ESTO VA A RENOMBRAR TUS ARCHIVOS A MINÚSCULAS. ¿Seguro? (s/n): ")
    if confirm.lower() == 's':
        normalizar_sistema_archivos()
    else:
        print("Cancelado.")