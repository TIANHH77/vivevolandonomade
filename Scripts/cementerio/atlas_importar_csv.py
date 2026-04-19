import sqlite3
import csv
import os

# --- CONFIGURACIÓN ---
ruta_db = r"F:\RECUPERADAS\atlas.db"
ruta_csv = r"F:\Scripts\zonas.csv"  # Asegúrate de guardar tu excel así aquí

def importar_gps_desde_csv():
    if not os.path.exists(ruta_csv):
        print(f"ERROR: No encuentro el archivo {ruta_csv}")
        print("Por favor guarda tu Excel como CSV en esa ruta.")
        return

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    
    print("=== Iniciando Importación desde CSV ===")
    
    contador_total = 0
    
    try:
        with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
            lector = csv.DictReader(f)
            # Normalizamos nombres de columnas por si acaso (quita espacios extra)
            lector.fieldnames = [field.strip() for field in lector.fieldnames]
            
            # Verifica que las columnas existan
            if 'zona' not in lector.fieldnames or 'gps_lat' not in lector.fieldnames:
                print(f"Error en CSV. Columnas encontradas: {lector.fieldnames}")
                print("El CSV debe tener columnas: zona, gps_lat, gps_lon")
                return

            for fila in lector:
                zona = fila['zona'].strip()
                try:
                    lat = float(fila['gps_lat'])
                    lon = float(fila['gps_lon'])
                except ValueError:
                    print(f"Saltando zona '{zona}': Coordenadas inválidas")
                    continue

                # El truco: Buscamos archivos cuya ruta contenga el nombre de la zona
                # Ejemplo: %\cejar\%
                patron = f"%\\{zona}\\%"
                
                cursor.execute("""
                    UPDATE selecciones 
                    SET gps_lat = ?, gps_lon = ? 
                    WHERE archivo LIKE ? 
                      AND (gps_lat IS NULL OR gps_lat = 0)
                """, (lat, lon, patron))
                
                afectados = cursor.rowcount
                if afectados > 0:
                    print(f"📍 Zona '{zona}': {afectados} fotos geolocalizadas.")
                    contador_total += afectados
                else:
                    print(f"⚠️ Zona '{zona}': No se encontraron fotos (¿Revisar nombre de carpeta?)")

        conn.commit()
        print(f"\n=== ÉXITO: {contador_total} fotos actualizadas en total ===")
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    importar_gps_desde_csv()