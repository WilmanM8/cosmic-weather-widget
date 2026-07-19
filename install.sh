#!/bin/bash

echo "=========================================="
echo " Instalando COSMIC Weather Widget..."
echo "=========================================="

# 1. Instalar dependencias del sistema (Debian/Ubuntu/Pop!_OS)
echo "-> Instalando dependencias del sistema (se requiere contraseña de sudo)..."
sudo apt update
sudo apt install -y python3-gi gir1.2-gtk-3.0 gir1.2-gtklayershell-0.1 python3-venv

# 2. Crear directorio de instalación en el espacio del usuario
INSTALL_DIR="$HOME/.local/share/cosmic-weather-widget"
echo "-> Copiando archivos a $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp weather_widget.py config_app.py weather_api.py "$INSTALL_DIR/"

# 3. Crear entorno virtual y usar dependencias del sistema
echo "-> Configurando entorno virtual de Python..."
cd "$INSTALL_DIR"
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install requests

# 4. Crear accesos directos (.desktop)
echo "-> Creando accesos directos..."
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

cat <<EOF > "$APPS_DIR/cosmic-weather-widget.desktop"
[Desktop Entry]
Name=COSMIC Weather Widget
Comment=Widget de clima transparente y moderno para el escritorio
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/weather_widget.py
Icon=weather-few-clouds
Terminal=false
Type=Application
Categories=Utility;DesktopSettings;
EOF

cat <<EOF > "$APPS_DIR/cosmic-weather-config.desktop"
[Desktop Entry]
Name=Configuración de Clima COSMIC
Comment=Ajustar el diseño, colores y tipografía del widget de clima
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/config_app.py
Icon=preferences-desktop-theme
Terminal=false
Type=Application
Categories=Utility;Settings;DesktopSettings;
EOF

# Autoarranque
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cp "$APPS_DIR/cosmic-weather-widget.desktop" "$AUTOSTART_DIR/"

echo "=========================================="
echo " ¡Instalación Completada con Éxito!"
echo "=========================================="
echo "Puedes abrir 'COSMIC Weather Widget' o 'Configuración de Clima COSMIC' desde tu menú de aplicaciones."
