# preferences.py
#
# Copyright 2019 Hugo Posnic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gio, Adw


UI_PATH = '/com/github/huluti/Curtail/ui/'
SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


@Gtk.Template(resource_path=UI_PATH + 'preferences.ui')
class CurtailPrefsDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'CurtailPrefsDialog'

    toggle_recursive = Gtk.Template.Child()
    toggle_metadata = Gtk.Template.Child()
    toggle_file_attributes = Gtk.Template.Child()
    toggle_new_file = Gtk.Template.Child()
    entry_suffix = Gtk.Template.Child()
    spin_timeout = Gtk.Template.Child()
    spin_png_lossy_level = Gtk.Template.Child()
    spin_png_lossless_level = Gtk.Template.Child()
    spin_webp_lossless_level = Gtk.Template.Child()
    spin_jpg_lossy_level = Gtk.Template.Child()
    spin_webp_lossy_level = Gtk.Template.Child()
    toggle_jpg_progressive = Gtk.Template.Child()
    toggle_svg_maximum_level = Gtk.Template.Child()

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.build_ui()

    def build_ui(self):
        # Compression settings

        # Recursive
        self.toggle_recursive.set_active(self._settings.get_boolean('recursive'))
        self.toggle_recursive.connect('notify::active', self.on_bool_changed,
                                     'recursive')

        # Keep metadata
        self.toggle_metadata.set_active(self._settings.get_boolean('metadata'))
        self.toggle_metadata.connect('notify::active', self.on_bool_changed,
                                     'metadata')

        # Preserve file attributes
        self.toggle_file_attributes.set_active(self._settings.get_boolean('file-attributes'))
        self.toggle_file_attributes.connect('notify::active', self.on_bool_changed,
                                     'file-attributes')

        # Use new file
        self.toggle_new_file.set_active(self._settings.get_boolean('new-file'))
        self.toggle_new_file.connect('notify::active', self.on_bool_changed,
                                     'new-file')

        # Suffix
        self.entry_suffix.set_sensitive(self._settings.get_boolean('new-file'))
        self.entry_suffix.set_text(self._settings.get_string('suffix'))
        self.entry_suffix.connect('changed', self.on_string_changed, 'suffix')

        # Compression Timeout
        self.spin_timeout.set_value(
            self._settings.get_int('compression-timeout'))
        self.spin_timeout.connect('value-changed',
            self.on_int_changed, 'compression-timeout')

        # PNG Lossy Compression Level
        self.spin_png_lossy_level.set_value(
            self._settings.get_int('png-lossy-level'))
        self.spin_png_lossy_level.connect('value-changed',
            self.on_int_changed, 'png-lossy-level')

        # PNG Lossless Compression Level
        self.spin_png_lossless_level.set_value(
            self._settings.get_int('png-lossless-level'))
        self.spin_png_lossless_level.connect('value-changed',
            self.on_int_changed, 'png-lossless-level')

        # WebP Lossless Compression Level
        self.spin_webp_lossless_level.set_value(
            self._settings.get_int('webp-lossless-level'))
        self.spin_webp_lossless_level.connect('value-changed',
            self.on_int_changed, 'webp-lossless-level')

        # JPG Lossy Compression Level
        self.spin_jpg_lossy_level.set_value(
            self._settings.get_int('jpg-lossy-level'))
        self.spin_jpg_lossy_level.connect('value-changed',
            self.on_int_changed, 'jpg-lossy-level')

        # WebP Lossy Compression Level
        self.spin_webp_lossy_level.set_value(
            self._settings.get_int('webp-lossy-level'))
        self.spin_webp_lossy_level.connect('value-changed',
            self.on_int_changed, 'webp-lossy-level')

        # Progressively Encode JPG
        self.toggle_jpg_progressive.set_active(self._settings.get_boolean('jpg-progressive'))
        self.toggle_jpg_progressive.connect('notify::active', self.on_bool_changed,
                                            'jpg-progressive')

        # Maxium SVG compression
        self.toggle_svg_maximum_level.set_active(self._settings.get_boolean('svg-maximum-level'))
        self.toggle_svg_maximum_level.connect('notify::active', self.on_bool_changed,
                                            'svg-maximum-level')

    def on_bool_changed(self, switch, state, key):
        self._settings.set_boolean(key, switch.get_active())
        # Additional actions
        if key == 'new-file':
            new_file = self._settings.get_boolean('new-file')
            self.parent.set_saving_subtitle(new_file)
            self.parent.show_warning_banner(not new_file)
            self.entry_suffix.set_sensitive(new_file)

    def on_string_changed(self, entry, key):
        self._settings.set_string(key, entry.get_text())
        if key == 'suffix':
            if not self._settings.get_string('suffix'):
                self._settings.reset('suffix')
            self.parent.set_saving_subtitle()

    def on_int_changed(self, spin, key):
        self._settings.set_int(key, spin.get_value())

