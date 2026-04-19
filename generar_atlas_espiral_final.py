import os
import json
import pandas as pd

# --- CONFIGURACIÓN RELATIVA (Funciona en cualquier PC/Disco) ---
DIR_FOTOS = "fotos"
CSV_ZONAS = os.path.join("data", "zonas.csv")
JSON_OUT = os.path.join("data", "puntos_mapa.json")

def limpiar_nombre_archivo(ruta_carpeta, nombre_original):
    """Limpia nombres con espacios para evitar errores en la web."""
    nuevo_nombre = nombre_original.replace(" ", "_").replace("+", "_").replace("__", "_").lower()
    if nuevo_nombre != nombre_original:
        try:
            os.rename(os.path.join(ruta_carpeta, nombre_original), os.path.join(ruta_carpeta, nuevo_nombre))
            return nuevo_nombre
        except Exception as e:
            print(f"⚠️ Error al renombrar {nombre_original}: {e}")
    return nombre_original

def limpiar_titulo(n):
    # 'miliciano_herido.webp' -> 'Miliciano herido'
    base = n.replace(".webp","").replace(".jpg","").replace(".jpeg","").replace("_", " ").split('(')[0].strip()
    return base.capitalize()

def generar_atlas():
    # 1. Cargar relatos existentes para no perder descripciones
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
        print(f"❌ Error crítico: No se encontró {CSV_ZONAS}\n{e}")
        return

    puntos_finales = []
    conteo_zonas = {}

    print(f"🛰️  Escaneando búnker en: {os.path.abspath(DIR_FOTOS)}...")
    
    for carpeta in os.listdir(DIR_FOTOS):
        ruta_completa = os.path.join(DIR_FOTOS, carpeta)
        if not os.path.isdir(ruta_completa): continue
        
        # Omitimos carpetas que no son para el mapa
        if carpeta in ["recortes", "panos", "assets_web", "nueva_carpeta"]: continue

        # Extraer zona (ej: pub_medellin -> zona: medellin, prefijo: pub)
        if "_" in carpeta:
            prefijo = carpeta.split("_")[0]
            zona_key = carpeta.split("_", 1)[1]
        else:
            zona_key = carpeta
            prefijo = ""

        if zona_key in zonas_dict:
            info_gps = zonas_dict[zona_key]
            
            # Clasificación de Capas
            capa_nombre = "Patrimonio Histórico"
            if prefijo == "nomad": capa_nombre = "Bitácora Nómada"
            elif prefijo == "fly": capa_nombre = "Vuelo Aéreo"
            elif prefijo == "narrativa": capa_nombre = "Narrativa Sonora"

            for archivo in os.listdir(ruta_completa):
                if archivo.lower().endswith((".webp", ".jpg", ".jpeg")):
                    archivo = limpiar_nombre_archivo(ruta_completa, archivo)
                    
                    foto_id = f"{zona_key}_{archivo.replace('.', '_')}"
                    
                    if foto_id in puntos_existentes:
                        punto = puntos_existentes[foto_id].copy()
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
                            "descripcion": info_gps.get('descripcion', f"Registro en {zona_key.capitalize()}."),
                            "relato": "Pendiente de relato..."
                        })
                    conteo_zonas[zona_key] = conteo_zonas.get(zona_key, 0) + 1

    # 4. Guardar JSON
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(puntos_finales, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*40)
    for z, c in sorted(conteo_zonas.items()):
        print(f"✅ Zona '{z}': {c} fotos sincronizadas.")
    print("="*40)
    print(f"🚀 ¡Misión cumplida! {len(puntos_finales)} puntos en el Atlas.")

if __name__ == "__main__":
    generar_atlas()