import sqlite3
import os

# --- CONFIGURACIÓN ---
ruta_db = r"F:\RECUPERADAS\atlas.db"

# Diccionario de zonas basado en tu imagen de Excel (Nombre carpeta: (Latitud, Longitud))
# He transcrito los datos de tu captura.
zonas_gps = {
    "cejar": (-23.100, -67.500),
    "chaxa": (-23.300, -67.500),
    "laguna_altipl": (-23.000, -67.800), # Nota: Ajusta si la carpeta se llama distinto, en tu excel decia laguna_tal pero en la carpeta parece laguna_altiplanica
    "lazcar": (-23.350, -67.750),
    "ojos_del_salar": (-23.500, -68.250),
    "peine": (-23.700, -68.050),
    "planta_litio": (-23.600, -68.300),
    "puritama": (-22.600, -68.000),
    "san_pedro": (-22.910, -68.200),
    "tara_": (-23.750, -67.500),
    "tatio": (-22.333, -68.017),
    "tebenquinche": (-23.300, -67.600),
    "valle_arco_iris": (-22.900, -68.300),
    "valle_de_la_luna": (-22.906, -68.243) # Ajusta esto si la carpeta tiene el nombre largo completo
}

# Nombres alternativos de carpetas (según vi en tus capturas de pantalla)
# Mapeamos el nombre de la carpeta real al nombre clave del diccionario de arriba
mapeo_carpetas = {
    "laguna_altiplanica": "laguna_altipl", 
    "valle_de_la_luna_y_valle_de_la_muerte": "valle_de_la_luna",
    "san_pedro_atacama": "san_pedro" # Por si acaso la carpeta padre tambien cuenta
}

def actualizar_gps_por_zonas():
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    
    contador_total = 0
    
    print("=== Iniciando Actualización de GPS por Zonas ===")

    # Unimos el diccionario base con el mapeo para iterar
    # Primero iteramos las zonas directas
    for carpeta, coords in zonas_gps.items():
        lat, lon = coords
        # El % al principio y final significa "cualquier texto antes o despues"
        # Buscamos archivos que contengan el nombre de la carpeta en su ruta
        query_str = f"%\\{carpeta}\\%" 
        
        cursor.execute("""
            UPDATE selecciones 
            SET gps_lat = ?, gps_lon = ? 
            WHERE archivo LIKE ? AND (gps_lat IS NULL OR gps_lat = 0)
        """, (lat, lon, query_str))
        
        cambios = cursor.rowcount
        if cambios > 0:
            print(f"Zona '{carpeta}': Actualizadas {cambios} fotos.")
            contador_total += cambios

    # Ahora iteramos las excepciones/nombres largos (del mapeo)
    for carpeta_real, clave_diccionario in mapeo_carpetas.items():
        if clave_diccionario in zonas_gps:
            lat, lon = zonas_gps[clave_diccionario]
            query_str = f"%\\{carpeta_real}\\%"
            
            cursor.execute("""
                UPDATE selecciones 
                SET gps_lat = ?, gps_lon = ? 
                WHERE archivo LIKE ? AND (gps_lat IS NULL OR gps_lat = 0)
            """, (lat, lon, query_str))
            
            cambios = cursor.rowcount
            if cambios > 0:
                print(f"Zona '{carpeta_real}': Actualizadas {cambios} fotos.")
                contador_total += cambios

    conn.commit()
    conn.close()
    print(f"\n=== Finalizado. Total fotos actualizadas: {contador_total} ===")

if __name__ == "__main__":
    actualizar_gps_por_zonas()