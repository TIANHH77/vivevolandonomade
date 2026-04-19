import os
import sqlite3
import pandas as pd

# --- RUTAS ---
BASE_ATLAS = r"C:\PROYECTOS\Atlas\vivevolandonomade"
DIR_FOTOS_WEB = os.path.join(BASE_ATLAS, "fotos")
DB_PATH = os.path.join(BASE_ATLAS, "data", "haroldo_indice.db")

def auditoria_unificada():
    print("🚀 Iniciando Auditoría sobre el Cerebro Unificado (60k registros)...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encuentra la DB en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    reporte = []

    # 1. Escanear fotos de la web
    print(f"📂 Analizando selección web en: {DIR_FOTOS_WEB}")
    
    for root, dirs, files in os.walk(DIR_FOTOS_WEB):
        for f in files:
            if f.lower().endswith(('.webp', '.jpg', '.jpeg')):
                # Nombre base (sin extensión)
                nombre_base = f.split('.')[0].lower()
                
                # 2. CONSULTA SQL MAESTRA
                # Buscamos en la VISTA que creamos antes
                query = """
                SELECT nombre_archivo, ruta_maestra, fuente_origen 
                FROM vista_maestra_originales 
                WHERE nombre_archivo LOWER LIKE ? 
                LIMIT 1
                """
                # Buscamos coincidencias parciales (por si el nombre original está contenido)
                cursor = conn.execute(query, (f'%{nombre_base}%',))
                res = cursor.fetchone()

                if res:
                    reporte.append({
                        "archivo_web": f,
                        "fuente": res[2],
                        "nombre_original": res[0],
                        "ruta_master": res[1],
                        "estado": "VINCULADO"
                    })
                else:
                    reporte.append({
                        "archivo_web": f,
                        "fuente": "N/A",
                        "nombre_original": "N/A",
                        "ruta_master": "N/A",
                        "estado": "HUÉRFANO"
                    })

    conn.close()

    # 3. Guardar Reporte
    if reporte:
        df_final = pd.DataFrame(reporte)
        output_path = os.path.join(BASE_ATLAS, "reporte_trazabilidad_final.csv")
        df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # Estadísticas
        vinculados = len(df_final[df_final['estado'] == 'VINCULADO'])
        print("\n" + "═"*40)
        print(f"✅ AUDITORÍA MAESTRA FINALIZADA")
        print(f"📸 Fotos web analizadas: {len(df_final)}")
        print(f"🔗 Vinculadas a un Master: {vinculados}")
        print(f"❓ Huérfanas (sin master): {len(df_final) - vinculados}")
        print(f"📄 Reporte: {output_path}")
        print("═"*40)

if __name__ == "__main__":
    auditoria_unificada()