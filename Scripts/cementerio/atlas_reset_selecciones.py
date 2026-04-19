import sqlite3

# Ajusta la ruta si tu DB está en otro lado
ruta_db = r"F:\RECUPERADAS\atlas.db"

def resetear_selecciones():
    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        
        # Contamos cuántos hay antes de borrar para saber
        cursor.execute("SELECT COUNT(*) FROM selecciones")
        antes = cursor.fetchone()[0]
        
        # Borramos todo el contenido de la tabla selecciones
        cursor.execute("DELETE FROM selecciones")
        
        # Reiniciamos el contador de IDs (opcional, pero ordenado)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='selecciones'")
        
        conn.commit()
        
        print(f"=== LIMPIEZA COMPLETADA ===")
        print(f"Se eliminaron {antes} registros antiguos de la tabla 'selecciones'.")
        print("La tabla está vacía y lista para recibir los nuevos nombres de carpeta.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    resetear_selecciones()