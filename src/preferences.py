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


UI_PATH = '/com/github/huluti/ImCompressor/ui/'
SETTINGS_SCHEMA = 'com.github.huluti.ImCompressor'


@Gtk.Template(resource_path=UI_PATH + 'preferences.ui')
class ImCompressorPrefsWindow(Gtk.Window):
    __gtype_name__ = 'ImCompressorPrefsWindow'

    grid = Gtk.Template.Child()
    toggle_new_file = Gtk.Template.Child()
    toggle_dark_theme = Gtk.Template.Child()

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent

        self.build_ui()

    def build_ui(self):
        # Use new file
        self.toggle_new_file.set_active(self._settings.get_boolean('new-file'))
        self.toggle_new_file.connect('notify::active', self.on_bool_changed,
                                     'new-file')
        # Toggle dark theme
        self.toggle_dark_theme.connect('notify::active', self.on_bool_changed,
                                       'dark-theme')
        self.toggle_dark_theme.set_active(self._settings.get_boolean('dark-theme'))

    def on_bool_changed(self, switch, state, key):
        self._settings.set_boolean(key, switch.get_active())
        if key == 'dark-theme':
            self.parent.toggle_dark_theme(switch.get_active())
        elif key == 'new-file':
            self.parent.change_treeview_label()
