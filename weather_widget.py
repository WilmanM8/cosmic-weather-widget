import sys
import gi
import threading
import json
import os

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib, Gio, PangoCairo
from weather_api import get_location, get_weather

CONFIG_DIR = os.path.expanduser("~/.config/cosmic-weather-widget")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_CONFIG = {
    "city": "auto",
    "margin_x": 50,
    "margin_y": 50,
    "bg_color": "rgb(30, 30, 30)",
    "bg_opacity": 0.6,
    "text_color": "rgba(255, 255, 255, 1.0)",
    "border_radius": 16,
    "font_family": "'Inter', 'Roboto', sans-serif",
    "icon_size": 48,
    "temp_size": 48,
    "desc_size": 18,
    "city_size": 14
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception as e:
        print(f"Error cargando config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error guardando config: {e}")

def extract_rgb(rgba_str):
    rgba = Gdk.RGBA()
    if rgba.parse(rgba_str):
        return int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
    return 30, 30, 30

def generate_css(config):
    r, g, b = extract_rgb(config.get("bg_color", "rgb(30, 30, 30)"))
    opacity = float(config.get("bg_opacity", 0.6))
    
    # Gradiente sutil para glassmorphism (ligeramente más claro arriba)
    top_opacity = min(1.0, opacity + 0.1)
    bottom_opacity = max(0.0, opacity - 0.1)
    bg_css = f"background: linear-gradient(135deg, rgba({r},{g},{b},{top_opacity}) 0%, rgba({r},{g},{b},{bottom_opacity}) 100%);"
    
    border_radius = config.get("border_radius", 16)
    font_family = config.get("font_family", "'Inter', 'Roboto', sans-serif")
    text_color = config.get("text_color", "rgba(255, 255, 255, 1.0)")
    
    icon_size = int(config.get("icon_size", 48))
    temp_size = int(config.get("temp_size", 48))
    desc_size = int(config.get("desc_size", 18))
    city_size = int(config.get("city_size", 14))

    return f"""
    window {{
        background-color: transparent;
    }}
    .widget-container, .widget-container * {{
        font-family: {font_family};
    }}
    .widget-container {{
        {bg_css}
        border-radius: {border_radius}px;
        /* Bordes iluminados simulando reflejo de cristal pulido */
        border-top: 1px solid rgba(255, 255, 255, 0.4);
        border-left: 1px solid rgba(255, 255, 255, 0.2);
        border-right: 1px solid rgba(0, 0, 0, 0.2);
        border-bottom: 1px solid rgba(0, 0, 0, 0.4);
        padding: 24px;
        margin: 10px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }}
    .weather-icon {{
        font-size: {icon_size}px;
        color: {text_color};
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    .temperature {{
        font-size: {temp_size}px;
        font-weight: 700;
        color: {text_color};
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    .weather-desc {{
        font-size: {desc_size}px;
        font-weight: 500;
        color: {text_color};
        margin-top: 5px;
    }}
    .city-label {{
        font-size: {city_size}px;
        font-weight: 400;
        color: {text_color};
        opacity: 0.8;
        margin-top: 5px;
    }}
    """

class WeatherWidget(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_app_paintable(True)
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        
        # Namespace para ayudar a que COSMIC aplique desenfoque si lo soporta
        GtkLayerShell.set_namespace(self, "weather_widget")
        
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)
        
        self.config = load_config()
        self.margin_x = self.config.get("margin_x", 50)
        self.margin_y = self.config.get("margin_y", 50)
        
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, self.margin_x)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, self.margin_y)
        
        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.apply_css()
        
        self.setup_file_monitor()
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.get_style_context().add_class("widget-container")
        self.add(self.box)
        
        self.top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.icon_label = Gtk.Label(label="⏳")
        self.icon_label.get_style_context().add_class("weather-icon")
        self.temp_label = Gtk.Label(label="--°C")
        self.temp_label.get_style_context().add_class("temperature")
        
        self.top_box.pack_start(self.icon_label, False, False, 0)
        self.top_box.pack_start(self.temp_label, False, False, 0)
        self.box.pack_start(self.top_box, False, False, 0)
        
        self.desc_label = Gtk.Label(label="Cargando...")
        self.desc_label.get_style_context().add_class("weather-desc")
        self.box.pack_start(self.desc_label, False, False, 0)
        
        self.city_label = Gtk.Label(label="Detectando ubicación...")
        self.city_label.get_style_context().add_class("city-label")
        self.box.pack_start(self.city_label, False, False, 0)
        
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | 
            Gdk.EventMask.BUTTON_RELEASE_MASK | 
            Gdk.EventMask.POINTER_MOTION_MASK | 
            Gdk.EventMask.BUTTON1_MOTION_MASK
        )
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)
        
        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        self.start_margin_x = 0
        self.start_margin_y = 0

        self.current_city = self.config.get("city", "auto")
        threading.Thread(target=self.fetch_weather_data, daemon=True).start()
        GLib.timeout_add(1800000, self.fetch_weather_data_timer)

    def apply_css(self):
        css_data = generate_css(self.config)
        self.css_provider.load_from_data(css_data.encode('utf-8'))

    def setup_file_monitor(self):
        try:
            gfile = Gio.File.new_for_path(CONFIG_FILE)
            self.monitor = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.monitor.connect("changed", self.on_config_changed)
        except Exception as e:
            print(f"Advertencia: No se pudo iniciar el monitoreo del archivo de configuración: {e}")

    def on_config_changed(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT or event_type == Gio.FileMonitorEvent.CREATED:
            GLib.idle_add(self.reload_config)

    def reload_config(self):
        try:
            PangoCairo.FontMap.get_default().changed()
        except Exception:
            pass
        self.config = load_config()
        self.apply_css()
        new_city = self.config.get("city", "auto")
        if new_city != self.current_city:
            self.current_city = new_city
            threading.Thread(target=self.fetch_weather_data, daemon=True).start()
        return False

    def on_button_press(self, widget, event):
        if event.button == 1: # Clic izquierdo para arrastrar
            self.dragging = True
            # Detectar si estamos bajo Wayland para usar el modo de arrastre relativo
            self.is_wayland = "wayland" in os.environ.get("XDG_SESSION_TYPE", "").lower() or "WAYLAND_DISPLAY" in os.environ
            
            if self.is_wayland:
                self.start_x = event.x
                self.start_y = event.y
            else:
                self.start_x = event.x_root
                self.start_y = event.y_root
                self.start_margin_x = self.margin_x
                self.start_margin_y = self.margin_y
        elif event.button == 3: # Clic derecho para menú
            self.show_context_menu(event)
        return True

    def show_context_menu(self, event):
        menu = Gtk.Menu()
        config_item = Gtk.MenuItem(label="⚙️ Abrir Configuración")
        config_item.connect("activate", lambda w: GLib.spawn_command_line_async("gtk-launch cosmic-weather-config"))
        menu.append(config_item)
        quit_item = Gtk.MenuItem(label="❌ Cerrar Widget")
        quit_item.connect("activate", Gtk.main_quit)
        menu.append(quit_item)
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def on_button_release(self, widget, event):
        if event.button == 1:
            if getattr(self, 'dragging', False):
                self.dragging = False
                self.config["margin_x"] = self.margin_x
                self.config["margin_y"] = self.margin_y
                save_config(self.config)
        return True

    def on_motion_notify(self, widget, event):
        if getattr(self, 'dragging', False):
            if getattr(self, 'is_wayland', False):
                # Arrastre relativo para Wayland (donde x_root/y_root no son globales)
                dx = event.x - self.start_x
                dy = event.y - self.start_y
                self.margin_x = int(self.margin_x + dx)
                self.margin_y = int(self.margin_y + dy)
            else:
                # Arrastre absoluto para X11
                dx = event.x_root - self.start_x
                dy = event.y_root - self.start_y
                self.margin_x = int(self.start_margin_x + dx)
                self.margin_y = int(self.start_margin_y + dy)
            
            if self.margin_x < 0: self.margin_x = 0
            if self.margin_y < 0: self.margin_y = 0
            
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, self.margin_x)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, self.margin_y)
        return True

    def fetch_weather_data_timer(self):
        threading.Thread(target=self.fetch_weather_data, daemon=True).start()
        return True

    def fetch_weather_data(self):
        loc = get_location(self.current_city)
        if not loc:
            GLib.idle_add(self.update_ui_error, "Error de ubicación")
            return
            
        weather = get_weather(loc['lat'], loc['lon'])
        if not weather:
            GLib.idle_add(self.update_ui_error, "Error de clima")
            return
            
        GLib.idle_add(self.update_ui_success, loc, weather)

    def update_ui_success(self, loc, weather):
        self.city_label.set_text(loc['city'])
        self.temp_label.set_text(f"{weather['temperature']}°C")
        self.icon_label.set_text(weather['icon'])
        self.desc_label.set_text(weather['description'])
        self.show_all()

    def update_ui_error(self, message):
        self.city_label.set_text(message)
        self.icon_label.set_text("⚠️")
        self.temp_label.set_text("--°C")
        self.desc_label.set_text("Intenta más tarde")
        self.show_all()

if __name__ == '__main__':
    win = WeatherWidget()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
