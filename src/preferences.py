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

from gi.repository import Gtk, Gio

from .tools import message_dialog


UI_PATH = '/com/github/huluti/Curtail/ui/'
SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


@Gtk.Template(resource_path=UI_PATH + 'preferences.ui')
class CurtailPrefsWindow(Gtk.Window):
    __gtype_name__ = 'CurtailPrefsWindow'

    toggle_metadata = Gtk.Template.Child()
    toggle_new_file = Gtk.Template.Child()
    new_file_label = Gtk.Template.Child()
    entry_suffix = Gtk.Template.Child()
    spin_png_lossy_level = Gtk.Template.Child()
    spin_png_lossless_level = Gtk.Template.Child()
    spin_webp_lossless_level = Gtk.Template.Child()
    spin_jpg_lossy_level = Gtk.Template.Child()
    spin_webp_lossy_level = Gtk.Template.Child()
    toggle_jpg_progressive = Gtk.Template.Child()
    toggle_dark_theme = Gtk.Template.Child()

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_transient_for(parent)
        self.set_modal(True)

        self.build_ui()

    def build_ui(self):
        # Compression settings

        # Use new file
        self.toggle_metadata.set_active(self._settings.get_boolean('metadata'))
        self.toggle_metadata.connect('notify::active', self.on_bool_changed,
                                     'metadata')

        # Keep metadata
        self.toggle_new_file.set_active(self._settings.get_boolean('new-file'))
        self.toggle_new_file.connect('notify::active', self.on_bool_changed,
                                     'new-file')

        # Suffix
        self.enable_suffix_section()
        self.entry_suffix.set_text(self._settings.get_string('suffix'))
        self.entry_suffix.connect('changed', self.on_string_changed, 'suffix')

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

        # WEBP Lossless Compression Level
        self.spin_webp_lossless_level.set_value(
            self._settings.get_int('webp-lossless-level'))
        self.spin_webp_lossless_level.connect('value-changed',
            self.on_int_changed, 'webp-lossless-level')

        # JPG Lossy Compression Level
        self.spin_jpg_lossy_level.set_value(
            self._settings.get_int('jpg-lossy-level'))
        self.spin_jpg_lossy_level.connect('value-changed',
            self.on_int_changed, 'jpg-lossy-level')

        # WEBP Lossy Compression Level
        self.spin_webp_lossy_level.set_value(
            self._settings.get_int('webp-lossy-level'))
        self.spin_webp_lossy_level.connect('value-changed',
            self.on_int_changed, 'webp-lossy-level')

        # Progressively Encode JPG
        self.toggle_jpg_progressive.set_active(self._settings.get_boolean('jpg-progressive'))
        self.toggle_jpg_progressive.connect('notify::active', self.on_bool_changed,
                                            'jpg-progressive')

        # Advanced settings

        # Toggle dark theme
        self.toggle_dark_theme.connect('notify::active', self.on_bool_changed,
                                       'dark-theme')
        self.toggle_dark_theme.set_active(
            self._settings.get_boolean('dark-theme'))

    def on_bool_changed(self, switch, state, key):
        self._settings.set_boolean(key, switch.get_active())
        # Additional actions
        if key == 'dark-theme':
            self.parent.toggle_dark_theme(switch.get_active())
        elif key == 'new-file':
            self.parent.change_save_info_label()
            self.enable_suffix_section()

    def on_string_changed(self, entry, key):
        self._settings.set_string(key, entry.get_text())
        if key == 'suffix':
            if not self._settings.get_string('suffix'):
                self._settings.reset('suffix')
            self.parent.change_save_info_label()

    def on_int_changed(self, spin, key):
        self._settings.set_int(key, spin.get_value())

    def enable_suffix_section(self):
        boolean = self._settings.get_boolean('new-file')
        self.new_file_label.set_sensitive(boolean)
        self.entry_suffix.set_sensitive(boolean)
