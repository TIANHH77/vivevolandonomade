import os

def mapear_bunker_detallado(ruta_raiz):
    print(f"\n🔍 ESCANEO DE RUTAS COMPLETAS: {ruta_raiz}")
    print("=" * 60)

    for raiz, carpetas, archivos in os.walk(ruta_raiz):
        # Filtros de exclusión: Git y la carpeta del legado pesado
        if '.git' in carpetas:
            carpetas.remove('.git')
        if 'legado_haroldo' in carpetas:
            carpetas.remove('legado_haroldo')

        # Solo procesamos si hay archivos en la carpeta actual
        if archivos:
            print(f"\n📂 Carpeta: {raiz}")
            for f in archivos:
                # Ignoramos el propio script para no ensuciar la lista
                if f != "revisar_atlas.py":
                    # Construimos la ruta completa
                    ruta_completa = os.path.join(raiz, f)
                    print(f"  📍 {ruta_completa}")

if __name__ == "__main__":
    # Forzamos que use la ruta donde estás parado (F:\ATLAS)
    ruta_actual = os.getcwd()
    mapear_bunker_detallado(ruta_actual)
    mapear_bunker_detallado(ruta_actual)