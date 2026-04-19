@echo off
echo INICIANDO ATLAS SUR DAO...
echo -----------------------------------
echo No cierres esta ventana negra mientras uses el mapa.
start http://localhost:8000
python -m http.server
pause