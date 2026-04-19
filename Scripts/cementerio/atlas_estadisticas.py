import sqlite3
import os

ruta_db = r"F:\RECUPERADAS\atlas.db"

def generar_reporte_camaras():
    if not os.path.exists(ruta_db):
        print("La base de datos aún no existe.")
        return

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT camara, COUNT(*) as total FROM solo_nikon GROUP BY camara ORDER BY total DESC")
        resultados = cursor.fetchall()
        
        print("\n" + "="*40)
        print("📊 RESUMEN DEL ARCHIVO HISTÓRICO")
        print("="*40)
        
        total_general = 0
        for camara, cantidad in resultados:
            print(f"📷 {camara:<15} : {cantidad:>5} fotos")
            total_general += cantidad
            
        print("-" * 40)
        print(f"🌟 TOTAL ARCHIVO FILETE : {total_general} fotos")
        print("="*40)

    except Exception as e:
        print(f"Aún no hay datos para procesar: {e}")
    
    conn.close()

if __name__ == "__main__":
    generar_reporte_camaras()