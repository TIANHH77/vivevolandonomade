import sqlite3
import os
import shutil
from datetime import datetime

# --- CONFIGURACIÓN ---
ruta_db = r"F:\RECUPERADAS\atlas.db"
# Aquí guardaremos el "Oro" limpio y ordenado
carpeta_destino_base = r"F:\RECUPERADAS\Coleccion_Nikon"

def obtener_anio_archivo(ruta_archivo):
    """Intenta sacar el año de modificación del archivo para crear la carpeta."""
    try:
        timestamp = os.path.getmtime(ruta_archivo)
        return datetime.fromtimestamp(timestamp).strftime('%Y')
    except:
        return "Sin_Fecha"

def ejecutar_rescate():
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Verificamos si ya terminó el escaneo anterior
    try:
        cursor.execute("SELECT COUNT(*) FROM solo_nikon")
        total_a_rescatar = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        print("⚠️ ERROR: La tabla 'solo_nikon' no existe aún.")
        print("Primero debes dejar terminar el script 'atlas_filtro_nikon.py'")
        return

    if total_a_rescatar == 0:
        print("No se encontraron fotos Nikon para rescatar todavía.")
        return

    print(f"=== INICIANDO OPERACIÓN RESCATE ===")
    print(f"Objetivo: Copiar {total_a_rescatar} fotos Nikon a {carpeta_destino_base}")
    print("Ordenando automáticamente por AÑO...")

    cursor.execute("SELECT ruta FROM solo_nikon")
    archivos = cursor.fetchall()

    contador = 0
    errores = 0

    for fila in archivos:
        ruta_origen = fila[0]
        nombre_archivo = os.path.basename(ruta_origen)
        
        if os.path.exists(ruta_origen):
            # 1. Averiguar el año para crear la subcarpeta
            anio = obtener_anio_archivo(ruta_origen)
            carpeta_final = os.path.join(carpeta_destino_base, anio)
            
            # 2. Crear carpeta si no existe (ej: .../Coleccion_Nikon/2015)
            os.makedirs(carpeta_final, exist_ok=True)
            
            ruta_destino = os.path.join(carpeta_final, nombre_archivo)

            # 3. Evitar sobreescribir si ya existe (añadir _copia)
            if os.path.exists(ruta_destino):
                nombre_sin_ext, ext = os.path.splitext(nombre_archivo)
                ruta_destino = os.path.join(carpeta_final, f"{nombre_sin_ext}_copia{ext}")

            try:
                # LA COPIA REAL
                shutil.copy2(ruta_origen, ruta_destino)
                contador += 1
                if contador % 100 == 0:
                    print(f"✅ Copiadas {contador} fotos... (Última: Año {anio})")
            except Exception as e:
                print(f"❌ Error copiando {nombre_archivo}: {e}")
                errores += 1
        else:
            print(f"⚠️ Archivo perdido (ya no está en disco): {ruta_origen}")

    conn.close()
    print("\n" + "="*40)
    print(f"🎉 MISIÓN CUMPLIDA")
    print(f"Fotos rescatadas: {contador}")
    print(f"Errores: {errores}")
    print(f"Ubicación: {carpeta_destino_base}")
    print("="*40)

if __name__ == "__main__":
    ejecutar_rescate()