#!/bin/bash

echo "Instalando dependencias de sistema para Pop!_OS (Ubuntu/Debian)..."
sudo apt-get update
# python3-gi provee PyGObject a nivel de sistema
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-venv libcairo2-dev libgirepository1.0-dev

echo "Creando entorno virtual con acceso a paquetes del sistema..."
python3 -m venv --system-site-packages venv

echo "Instalando dependencias de Python..."
source venv/bin/activate
pip install --upgrade pip
pip install requests

echo "¡Entorno preparado! Para ejecutar:"
echo "source venv/bin/activate"
echo "python weather_widget.py"
