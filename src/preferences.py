from gi.repository import Gtk, Adw

from .settings_manager import SettingsManager


UI_PATH = "/com/github/huluti/Curtail/ui/"


@Gtk.Template(resource_path=UI_PATH + "preferences.ui")
class CurtailPrefsDialog(Adw.PreferencesDialog):
    __gtype_name__ = "CurtailPrefsDialog"

    toggle_recursive = Gtk.Template.Child()
    toggle_metadata = Gtk.Template.Child()
    toggle_file_attributes = Gtk.Template.Child()
    toggle_new_file = Gtk.Template.Child()
    toggle_naming_mode = Gtk.Template.Child()
    entry_suffix_prefix = Gtk.Template.Child()
    spin_timeout = Gtk.Template.Child()
    spin_png_lossy_level = Gtk.Template.Child()
    spin_png_lossless_level = Gtk.Template.Child()
    spin_webp_lossless_level = Gtk.Template.Child()
    spin_jpg_lossy_level = Gtk.Template.Child()
    spin_webp_lossy_level = Gtk.Template.Child()
    toggle_jpg_progressive = Gtk.Template.Child()
    toggle_svg_maximum_level = Gtk.Template.Child()

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.settings = SettingsManager()

        self.parent = parent
        self.build_ui()

    def build_ui(self):
        # Compression settings

        # Recursive
        self.toggle_recursive.set_active(self.settings.recursive)
        self.toggle_recursive.connect(
            "notify::active", self.on_bool_changed, "recursive"
        )

        # Keep metadata
        self.toggle_metadata.set_active(self.settings.metadata)
        self.toggle_metadata.connect("notify::active", self.on_bool_changed, "metadata")

        # Preserve file attributes
        self.toggle_file_attributes.set_active(self.settings.file_attributes)
        self.toggle_file_attributes.connect(
            "notify::active", self.on_bool_changed, "file-attributes"
        )

        # Use new file
        self.toggle_new_file.set_active(self.settings.new_file)
        self.toggle_new_file.connect("notify::active", self.on_bool_changed, "new-file")

        # Naming mode
        self.toggle_naming_mode.set_sensitive(self.settings.new_file)
        self.toggle_naming_mode.set_selected(self.settings.naming_mode)
        self.toggle_naming_mode.connect(
            "notify::selected-item", self.on_selected_item, "naming-mode"
        )

        # Prefix-Suffix
        self.entry_suffix_prefix.set_sensitive(self.settings.new_file)
        self.entry_suffix_prefix.set_text(self.settings.suffix_prefix)
        self.entry_suffix_prefix.connect(
            "changed", self.on_string_changed, "suffix-prefix"
        )

        # Compression Timeout
        self.spin_timeout.set_value(self.settings.compression_timeout)
        self.spin_timeout.connect(
            "notify::value", self.on_int_changed, "compression-timeout"
        )

        # PNG Lossless Compression Level
        self.spin_png_lossless_level.set_value(self.settings.png_lossless_level)
        self.spin_png_lossless_level.connect(
            "notify::value", self.on_int_changed, "png-lossless-level"
        )

        # PNG Lossy Compression Level
        self.spin_png_lossy_level.set_value(self.settings.png_lossy_level)
        self.spin_png_lossy_level.connect(
            "notify::value", self.on_int_changed, "png-lossy-level"
        )

        # WebP Lossless Compression Level
        self.spin_webp_lossless_level.set_value(self.settings.webp_lossless_level)
        self.spin_webp_lossless_level.connect(
            "notify::value", self.on_int_changed, "webp-lossless-level"
        )

        # WebP Lossy Compression Level
        self.spin_webp_lossy_level.set_value(self.settings.webp_lossy_level)
        self.spin_webp_lossy_level.connect(
            "notify::value", self.on_int_changed, "webp-lossy-level"
        )

        # JPG Lossy Compression Level
        self.spin_jpg_lossy_level.set_value(self.settings.jpg_lossy_level)
        self.spin_jpg_lossy_level.connect(
            "notify::value", self.on_int_changed, "jpg-lossy-level"
        )

        # Progressively Encode JPG
        self.toggle_jpg_progressive.set_active(self.settings.jpg_progressive)
        self.toggle_jpg_progressive.connect(
            "notify::active", self.on_bool_changed, "jpg-progressive"
        )

        # Maxium SVG compression
        self.toggle_svg_maximum_level.set_active(self.settings.svg_maximum_level)
        self.toggle_svg_maximum_level.connect(
            "notify::active", self.on_bool_changed, "svg-maximum-level"
        )

    def on_bool_changed(self, switch, state, key):
        self.settings.set_boolean(key, switch.get_active())
        # Additional actions
        if key == "new-file":
            new_file = self.settings.new_file
            self.parent.set_saving_subtitle(new_file)
            self.parent.show_warning_banner(not new_file)
            self.toggle_naming_mode.set_sensitive(new_file)
            self.entry_suffix_prefix.set_sensitive(new_file)

    def on_selected_item(self, combo, _, key):
        self.settings.set_int(key, combo.get_selected())
        if key == "naming-mode":
            if not self.settings.naming_mode:
                self.settings.reset("naming-mode")
            self.parent.set_saving_subtitle()

    def on_string_changed(self, entry, key):
        self.settings.set_string(key, entry.get_text())
        if key == "suffix-prefix":
            if not self.settings.suffix_prefix:
                self.settings.reset("suffix-prefix")
            self.parent.set_saving_subtitle()

    def on_int_changed(self, spin, _, key):
        self.settings.set_int(key, spin.get_value())
