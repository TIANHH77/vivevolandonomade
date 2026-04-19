import sqlite3
import os

conn_gps = sqlite3.connect('haroldo_indice.db')
conn_susto = sqlite3.connect('indice_fotos.db')

# Crear columna si no existe
try:
    conn_gps.execute("ALTER TABLE inventario ADD COLUMN Categoria TEXT")
except: pass

print("Extrayendo categorías del disco de 28TB...")
cursor_s = conn_susto.cursor()
cursor_s.execute("SELECT ruta FROM fotos")

mapa_categorias = {}
for (ruta,) in cursor_s.fetchall():
    nombre = os.path.basename(ruta)
    partes = ruta.split('\\')
    if len(partes) > 1:
        cat = partes[1]
        if "202" not in cat: # Filtramos para no usar el año como categoría
            mapa_categorias[nombre] = cat

print("Etiquetando archivos en el Atlas...")
cursor_g = conn_gps.cursor()
for nombre, categoria in mapa_categorias.items():
    cursor_g.execute("UPDATE inventario SET Categoria = ? WHERE Nombre = ?", (categoria, nombre))

conn_gps.commit()
print("¡Categorías rescatadas con éxito!")
conn_gps.close()
conn_susto.close()