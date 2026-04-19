import sqlite3

ruta_db = r"F:\RECUPERADAS\atlas.db"
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Consulta: contar archivos curados por zona
cursor.execute("""
    SELECT zona, COUNT(*) as cantidad
    FROM selecciones
    WHERE estado = 'curado'
    GROUP BY zona
    ORDER BY cantidad DESC
""")

resultados = cursor.fetchall()

print("=== REPORTE DE ZONAS CURADAS ===")
for zona, cantidad in resultados:
    print(f"{zona}: {cantidad} archivos enriquecidos")

conn.close()
