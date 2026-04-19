import os
import json
import pandas as pd

# --- CONFIGURACIÓN ---
DIR_FOTOS = r"F:\fotos"
CSV_ZONAS = r"F:\data\zonas.csv"
JSON_OUT = r"F:\data\puntos_mapa.json"

def limpiar_nombre_archivo(ruta_carpeta, nombre_original):
    """Limpia nombres con espacios, tildes o símbolos para evitar errores web."""
    nuevo_nombre = nombre_original.replace(" ", "_").replace("+", "_").replace("__", "_").lower()
    if nuevo_nombre != nombre_original:
        try:
            os.rename(os.path.join(ruta_carpeta, nombre_original), os.path.join(ruta_carpeta, nuevo_nombre))
            return nuevo_nombre
        except Exception as e:
            print(f"⚠️ No se pudo renombrar {nombre_original}: {e}")
            return nombre_original
    return nombre_original

def limpiar_titulo(n):
    # 'miliciano_herido.webp' -> 'Miliciano herido'
    base = n.replace(".webp","").replace("_", " ").split('(')[0].strip()
    return base.capitalize()

def generar_atlas():
    # 1. Cargar relatos existentes
    puntos_existentes = {}
    if os.path.exists(JSON_OUT):
        try:
            with open(JSON_OUT, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                puntos_existentes = {p['id']: p for p in datos}
        except:
            print("⚠️ Creando nuevo JSON de datos.")

    # 2. Cargar coordenadas del CSV
    try:
        df_zonas = pd.read_csv(CSV_ZONAS)
        zonas_dict = df_zonas.set_index('zona').to_dict('index')
    except Exception as e:
        print(f"❌ Error crítico: No se encontró el CSV en {CSV_ZONAS}\n{e}")
        return

    puntos_finales = []
    conteo_zonas = {}

    # 3. Escanear carpetas
    print("🛰️  Iniciando escaneo de búnker de fotos...")
    
    for carpeta in os.listdir(DIR_FOTOS):
        ruta_completa = os.path.join(DIR_FOTOS, carpeta)
        if not os.path.isdir(ruta_completa): continue

        # Extraer zona (ej: pub_medellin -> medellin)
        if "_" in carpeta:
            prefijo = carpeta.split("_")[0]
            zona_key = carpeta.split("_", 1)[1]
        else:
            continue

        if zona_key in zonas_dict:
            info_gps = zonas_dict[zona_key]
            
            # Asignar nombre de capa amigable
            capa_nombre = "Patrimonio"
            if prefijo == "nomad": capa_nombre = "Bitácora Nómada"
            elif prefijo == "fly": capa_nombre = "Vuelo Aéreo"
            elif prefijo == "narrativa": capa_nombre = "Narrativa Sonora"

            for archivo in os.listdir(ruta_completa):
                if archivo.lower().endswith(".webp"):
                    # LIMPIEZA AUTOMÁTICA DE NOMBRE
                    archivo = limpiar_nombre_archivo(ruta_completa, archivo)
                    
                    foto_id = f"{zona_key}_{archivo}"
                    
                    if foto_id in puntos_existentes:
                        punto = puntos_existentes[foto_id]
                        # Actualizamos solo lo técnico, mantenemos el relato
                        punto["lat"] = info_gps['lat']
                        punto["lon"] = info_gps['lon']
                        punto["capa"] = capa_nombre
                        punto["thumb"] = f"fotos/{carpeta}/{archivo}"
                        punto["full"] = f"fotos/{carpeta}/{archivo}"
                        puntos_finales.append(punto)
                    else:
                        puntos_finales.append({
                            "id": foto_id,
                            "lat": info_gps['lat'],
                            "lon": info_gps['lon'],
                            "zona": zona_key,
                            "capa": capa_nombre,
                            "titulo": limpiar_titulo(archivo),
                            "thumb": f"fotos/{carpeta}/{archivo}",
                            "full": f"fotos/{carpeta}/{archivo}",
                            "rating": 5,
                            "descripcion": info_gps['descripcion'],
                            "relato": "Pendiente de relato..."
                        })
                    conteo_zonas[zona_key] = conteo_zonas.get(zona_key, 0) + 1

    # 4. Guardar
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(puntos_finales, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*40)
    for z, c in conteo_zonas.items():
        print(f"✅ Zona '{z}': {c} fotos sincronizadas.")
    print("="*40)
    print(f"🚀 ¡Misión cumplida! {len(puntos_finales)} puntos totales en el Atlas.")

if __name__ == "__main__":
    generar_atlas()