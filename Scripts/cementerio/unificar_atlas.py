import os
import pandas as pd
import json

# ==========================================
# 🛠️ CONFIGURACIÓN DE RUTAS Y CATEGORÍAS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_FOTOS = os.path.join(BASE_DIR, "fotos")
RUTA_CSV = os.path.join(BASE_DIR, "data", "zonas.csv")
ARCHIVO_SALIDA = os.path.join(BASE_DIR, "data", "puntos_mapa.json")

# Diccionario de prefijos -> Nombres bonitos para el Atlas
CATEGORIAS = {
    "pub_": "Crónica & Etnografía",
    "nomad_": "Bitácora Nómada",
    "fly_": "Registro Aéreo",
    "nav_": "Registro Naval"
}

# Extensiones de imagen que vamos a indexar
EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

def escanear_todo():
    print("🚀 Iniciando Protocolo de Sincronización SUR DAO...")

    if not os.path.exists(RUTA_CSV):
        print(f"❌ ERROR: No se encuentra el archivo maestro en: {RUTA_CSV}")
        return

    # 1. CARGAR Y NORMALIZAR CSV
    try:
        df_zonas = pd.read_csv(RUTA_CSV)
        # Limpieza profunda: quitamos espacios, pasamos a minúsculas y reemplazamos espacios por guiones
        # El .str es vital para que Pandas sepa que operamos sobre texto
        df_zonas['zona_norm'] = df_zonas['zona'].astype(str).str.strip().str.lower().str.replace(" ", "_")
        
        # Mapa de búsqueda: { 'san_pedro': {lat, lon, desc, nombre_bonito}, ... }
        info_zonas = {}
        for _, row in df_zonas.iterrows():
            clave = row['zona_norm']
            info_zonas[clave] = {
                'nombre_real': row['zona'],
                'lat': float(row['lat']), 
                'lon': float(row['lon']), 
                'desc': row['descripcion']
            }
    except Exception as e:
        print(f"❌ Error procesando el CSV: {e}")
        return

    todos_los_puntos = []

    # 2. ESCANEO DEL DISCO (F:\fotos)
    for root, dirs, files in os.walk(RUTA_FOTOS):
        carpeta_actual = os.path.basename(root)
        nombre_lower = carpeta_actual.lower()
        
        # Por defecto
        zona_detectada = nombre_lower
        categoria_detectada = "Archivo General"
        
        # Identificar categoría por prefijo (pub_, fly_, etc)
        for prefijo, nombre_cat in CATEGORIAS.items():
            if nombre_lower.startswith(prefijo):
                categoria_detectada = nombre_cat
                zona_detectada = nombre_lower.replace(prefijo, "")
                break
        
        # 3. EMPAREJAMIENTO (Match con el CSV)
        if zona_detectada in info_zonas:
            datos = info_zonas[zona_detectada]
            
            # Filtramos solo imágenes reales
            fotos_validas = [f for f in files if f.lower().endswith(EXTS) and not f.startswith(".")]
            
            if fotos_validas:
                print(f"  ✅ Sincronizado: {datos['nombre_real']} [{categoria_detectada}] -> {len(fotos_validas)} fotos.")
            
            for foto in fotos_validas:
                # Construimos la ruta relativa para la web (GitHub usa '/')
                ruta_completa = os.path.join(root, foto)
                ruta_relativa = os.path.relpath(ruta_completa, BASE_DIR).replace("\\", "/")
                
                todos_los_puntos.append({
                    "id": foto,
                    "zona": zona_detectada,
                    "titulo": datos['nombre_real'],
                    "capa": categoria_detectada,
                    "lat": datos['lat'],
                    "lon": datos['lon'],
                    "thumb": ruta_relativa,
                    "descripcion": datos['desc']
                })

    # 4. GUARDAR RESULTADOS
    try:
        with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(todos_los_puntos, f, indent=4, ensure_ascii=False)
        print(f"\n✨ ÉXITO: Atlas actualizado con {len(todos_los_puntos)} registros en {ARCHIVO_SALIDA}")
    except Exception as e:
        print(f"❌ Error al guardar el JSON: {e}")

if __name__ == "__main__":
    escanear_todo()