import sys
import json
import os
# pyrefly: ignore [missing-import]
import gi

gi.require_version('Gtk', '3.0')
# pyrefly: ignore [missing-import]
from gi.repository import Gtk, Gdk

CONFIG_DIR = os.path.expanduser("~/.config/cosmic-weather-widget")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def rgb_to_gdk(rgb_str):
    rgba = Gdk.RGBA()
    if rgba.parse(rgb_str):
        return rgba
    return Gdk.RGBA(0,0,0,1)

class ConfigApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Configuración de Clima COSMIC")
        self.set_default_size(500, 600)
        self.set_border_width(20)
        self.apply_css()

        self.config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)

        # Usar ScrolledWindow para que quepa todo
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(vbox)
        self.add(scroll)

        # --- Ciudad ---
        hbox_city = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_city.pack_start(Gtk.Label(label="Ciudad:"), False, False, 0)
        self.city_entry = Gtk.Entry()
        self.city_entry.set_text(self.config.get("city", "auto"))
        self.city_entry.connect("changed", self.on_changed)
        hbox_city.pack_start(self.city_entry, True, True, 0)
        vbox.pack_start(hbox_city, False, False, 0)

        # --- Color de Fondo ---
        hbox_bg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_bg.pack_start(Gtk.Label(label="Color de Fondo:"), False, False, 0)
        self.bg_color_btn = Gtk.ColorButton()
        self.bg_color_btn.set_use_alpha(False)
        self.bg_color_btn.set_rgba(rgb_to_gdk(self.config.get("bg_color", "rgb(30, 30, 30)")))
        self.bg_color_btn.connect("color-set", self.on_changed)
        hbox_bg.pack_start(self.bg_color_btn, False, False, 0)
        vbox.pack_start(hbox_bg, False, False, 0)

        # --- Opacidad del Fondo ---
        hbox_opacity = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_opacity.pack_start(Gtk.Label(label="Opacidad (Cristal):"), False, False, 0)
        self.opacity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.05)
        self.opacity_scale.set_value(float(self.config.get("bg_opacity", 0.6)))
        self.opacity_scale.connect("value-changed", self.on_changed)
        hbox_opacity.pack_start(self.opacity_scale, True, True, 0)
        vbox.pack_start(hbox_opacity, False, False, 0)

        # --- Color de Texto ---
        hbox_text = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_text.pack_start(Gtk.Label(label="Color del Texto:"), False, False, 0)
        self.text_color_btn = Gtk.ColorButton()
        self.text_color_btn.set_use_alpha(True)
        self.text_color_btn.set_rgba(rgb_to_gdk(self.config.get("text_color", "rgba(255, 255, 255, 1.0)")))
        self.text_color_btn.connect("color-set", self.on_changed)
        hbox_text.pack_start(self.text_color_btn, False, False, 0)
        vbox.pack_start(hbox_text, False, False, 0)

        # --- Bordes Redondeados ---
        hbox_border = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_border.pack_start(Gtk.Label(label="Bordes Redondeados (px):"), False, False, 0)
        self.border_spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.border_spin.set_value(self.config.get("border_radius", 16))
        self.border_spin.connect("value-changed", self.on_changed)
        hbox_border.pack_start(self.border_spin, False, False, 0)
        vbox.pack_start(hbox_border, False, False, 0)

        vbox.pack_start(Gtk.Separator(), False, False, 10)

        # --- Fuente ---
        hbox_font = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_font.pack_start(Gtk.Label(label="Estilo de Letra:"), False, False, 0)
        self.font_combo = Gtk.ComboBoxText()
        fonts = {
            "'Inter', 'Roboto', sans-serif": "Moderna (Predeterminada)",
            "'digital-7', sans-serif": "Digital-7 (Dafont LCD Clásico)",
            "'Share Tech Mono', monospace": "Reloj Monocromo",
            "'Orbitron', sans-serif": "Reloj Digital Futurista",
            "'Press Start 2P', monospace": "Retro Pixel Art"
        }
        for font_css, font_name in fonts.items():
            self.font_combo.append(font_css, font_name)
        
        self.font_entry = Gtk.Entry()
        self.font_entry.set_text(self.config.get("font_family", "'Inter', 'Roboto', sans-serif"))
        self.font_entry.connect("changed", self.on_changed)
        
        active_id = -1
        current_font = self.config.get("font_family", "'Inter', 'Roboto', sans-serif")
        for i, font_css in enumerate(fonts.keys()):
            if font_css == current_font:
                active_id = i
                break
        if active_id != -1:
            self.font_combo.set_active(active_id)
            
        self.font_combo.connect("changed", self.on_font_combo_changed)
        hbox_font.pack_start(self.font_combo, False, False, 0)
        vbox.pack_start(hbox_font, False, False, 0)
        
        hbox_font_custom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_font_custom.pack_start(Gtk.Label(label="Fuente CSS manual:"), False, False, 0)
        hbox_font_custom.pack_start(self.font_entry, True, True, 0)
        
        # Botón para importar fuente
        import_btn = Gtk.Button(label="📥 Subir Archivo (.ttf/.otf)")
        import_btn.connect("clicked", self.on_import_font)
        hbox_font_custom.pack_start(import_btn, False, False, 0)
        
        vbox.pack_start(hbox_font_custom, False, False, 0)

        vbox.pack_start(Gtk.Separator(), False, False, 10)

        # --- Tamaños de Letra ---
        self.add_size_control(vbox, "Tamaño del Icono:", "icon_size", 48)
        self.add_size_control(vbox, "Tamaño de Temperatura:", "temp_size", 48)
        self.add_size_control(vbox, "Tamaño de Descripción:", "desc_size", 18)
        self.add_size_control(vbox, "Tamaño de Ciudad:", "city_size", 14)

        vbox.pack_start(Gtk.Separator(), False, False, 10)

        # --- Botón para Cerrar el Widget ---
        close_btn = Gtk.Button(label="Cerrar y salir del Widget del Escritorio")
        close_btn.get_style_context().add_class("close-widget-button")
        close_btn.connect("clicked", self.on_close_widget)
        vbox.pack_start(close_btn, False, False, 10)

    def add_size_control(self, container, label_text, config_key, default_val):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.pack_start(Gtk.Label(label=label_text), False, False, 0)
        spin = Gtk.SpinButton.new_with_range(10, 200, 1)
        spin.set_value(int(self.config.get(config_key, default_val)))
        spin.connect("value-changed", lambda s: self.on_size_changed(config_key, int(s.get_value())))
        hbox.pack_start(spin, False, False, 0)
        container.pack_start(hbox, False, False, 0)

    def on_size_changed(self, key, value):
        self.config[key] = value
        self.save_to_file()

    def on_import_font(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar Fuente (.ttf, .otf)",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_font = Gtk.FileFilter()
        filter_font.set_name("Fuentes")
        filter_font.add_pattern("*.ttf")
        filter_font.add_pattern("*.otf")
        filter_font.add_pattern("*.TTF")
        filter_font.add_pattern("*.OTF")
        dialog.add_filter(filter_font)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            filename = os.path.basename(filepath)
            
            fonts_dir = os.path.expanduser("~/.local/share/fonts/cosmic-weather-fonts")
            os.makedirs(fonts_dir, exist_ok=True)
            
            dest_path = os.path.join(fonts_dir, filename)
            
            import shutil
            shutil.copy2(filepath, dest_path)
            
            # Refrescar cache de fuentes del sistema
            os.system("fc-cache -f")
            
            # Obtener el nombre real de la familia usando fc-scan
            import subprocess
            try:
                result = subprocess.run(["fc-scan", "--format", "%{family}\\n", dest_path], capture_output=True, text=True)
                # fc-scan a veces devuelve "Familia,OtraFamilia". Tomamos la primera.
                actual_font_name = result.stdout.strip().split(',')[0].strip()
            except Exception:
                actual_font_name = os.path.splitext(filename)[0]
            
            if not actual_font_name:
                actual_font_name = os.path.splitext(filename)[0]
                
            # Formatearlo para el CSS y actualizar
            css_font = f"'{actual_font_name}', sans-serif"
            self.font_entry.set_text(css_font)
            
        dialog.destroy()

    def on_close_widget(self, button):
        os.system("pkill -f weather_widget.py")

    def apply_css(self):
        try:
            screen = Gdk.Screen.get_default()
            if screen is not None:
                css = b"""
                .close-widget-button {
                    background-image: none;
                    background-color: #000000;
                    color: #ffffff;
                    border: 2px solid #808080;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                .close-widget-button:hover {
                    background-image: none;
                    background-color: #d3d3d3;
                    color: #000000;
                    border: 2px solid #000000;
                }
                """
                provider = Gtk.CssProvider()
                provider.load_from_data(css)
                Gtk.StyleContext.add_provider_for_screen(
                    screen,
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el CSS personalizado ({e})", file=sys.stderr)

    def on_font_combo_changed(self, combo):
        font_id = combo.get_active_id()
        if font_id:
            self.font_entry.set_text(font_id)

    def on_changed(self, widget):
        self.config["city"] = self.city_entry.get_text()
        
        # Color de fondo (ignorando alpha del boton, usamos el slider)
        bg_rgba = self.bg_color_btn.get_rgba()
        self.config["bg_color"] = f"rgb({int(bg_rgba.red*255)}, {int(bg_rgba.green*255)}, {int(bg_rgba.blue*255)})"
        
        self.config["bg_opacity"] = round(self.opacity_scale.get_value(), 2)
        self.config["text_color"] = self.text_color_btn.get_rgba().to_string()
        self.config["border_radius"] = int(self.border_spin.get_value())
        self.config["font_family"] = self.font_entry.get_text()
        
        self.save_to_file()

    def save_to_file(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

if __name__ == '__main__':
    win = ConfigApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
