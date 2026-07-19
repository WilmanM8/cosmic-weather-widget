# COSMIC Weather Widget 🌤️

Un widget de clima elegante, transparente y nativo para entornos **Wayland** (especialmente diseñado para **Pop!_OS COSMIC** y similares). Creado con Python, GTK3 y `gtk-layer-shell`.

<img width="467" height="339" alt="widget" src="https://github.com/user-attachments/assets/c27f85b8-1e2d-453a-9f4b-9498490b6cf3" />
<img width="590" height="661" alt="conf-widget" src="https://github.com/user-attachments/assets/f54bfa26-0ae8-40f0-9dec-2018b382de86" />


## ✨ Características Principales
* **Nativo y Transparente:** Utiliza el protocolo Wayland Layer Shell para anclarse directamente al escritorio, sin botones de ventana, sin bordes y sin aparecer en la barra de tareas.
* **Glassmorphism Simulado:** Cuenta con reflejos asimétricos, sombras y gradientes translúcidos que simulan una hoja de cristal pulido sobre tu fondo de escritorio.
* **Panel de Configuración Completo (GUI):** Incluye una aplicación hermana gráfica (`config_app.py`) que te permite ajustar:
  * El color de fondo y su **nivel de transparencia**.
  * El color del texto.
  * El tamaño individual del icono y de la tipografía.
  * Los bordes redondeados.
* **Soporte de Tipografías Dinámico:** Elige entre fuentes preinstaladas (Moderno, Reloj Digital, Pixel Art) o **sube tu propio archivo `.ttf`** directamente desde la aplicación de configuración. El widget se actualiza en tiempo real.
* **Drag & Drop:** Haz **clic izquierdo** en el widget y arrástralo a cualquier lugar de la pantalla. Su posición se guarda automáticamente.
* **Ubicación Inteligente:** Detecta tu ciudad automáticamente por IP, o permítete escribir manualmente el nombre de tu ciudad.

## 🚀 Instalación (Para Usuarios Finales)

Para instalar y comenzar a usar este widget en tu sistema Linux (Debian/Ubuntu/Pop!_OS):

1. Clona este repositorio o descarga el código fuente:
   ```bash
   git clone https://github.com/WilmanM8/cosmic-weather-widget.git
   cd cosmic-weather-widget
   ```

2. Ejecuta el instalador automático:
   ```bash
   ./install.sh
   ```
   *(Te pedirá contraseña de `sudo` una sola vez para instalar las dependencias necesarias de GTK y Python en tu sistema).*

3. ¡Listo! Busca **"COSMIC Weather Widget"** en tu menú de aplicaciones y ábrelo. También se ha añadido al inicio automático para que arranque cuando enciendas tu PC.

## ⚙️ Uso y Configuración

1. **Para moverlo:** Mantén presionado el **clic izquierdo** sobre el widget y arrástralo.
2. **Para configurarlo:** Haz **clic derecho** sobre el widget y selecciona "Abrir Configuración", o busca **"Configuración de Clima COSMIC"** en tu menú de aplicaciones.
3. **Para cerrarlo:** Haz clic derecho sobre él y selecciona "Cerrar Widget".

## 🛠️ Tecnologías Utilizadas
* Python 3
* PyGObject (GTK3)
* `gtk-layer-shell` (Para integración nativa con Wayland)
* API de Clima: Open-Meteo (Gratuita y sin necesidad de API Key)
