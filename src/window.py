# window.py
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


UI_PATH = '/com/github/ImCompressor/ui/'


@Gtk.Template(resource_path=UI_PATH + 'window.ui')
class ImCompressorWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'ImCompressorWindow'

    headerbar = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.build_ui()
        self.create_actions()

    def build_ui(self):
        builder = Gtk.Builder.new_from_resource(UI_PATH + 'menu.ui')
        window_menu = builder.get_object('window-menu')
        menu_button = self.headerbar.get_children()[0]
        menu_button.set_menu_model(window_menu)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.add_accelerator(shortcut, 'win.' + action_name, None)

    def create_actions(self):
        self.create_simple_action('about', self.about_window)

    def about_window(self, *args):
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_logo_icon_name('com.github.ImCompressor')
        dialog.set_program_name('ImCompressor')
        dialog.set_version('0.1')
        dialog.set_website('https://github.com/Huluti/ImCompressor')
        dialog.set_authors(['Hugo Posnic'])
        dialog.set_comments(_("Simple & versatile image editor"))
        text = _("Distributed under the GNU GPL(v3) license.\n")
        text += 'https://github.com/Huluti/ImCompressor/blob/master/COPYING\n'
        dialog.set_license(text)
        dialog.run()
        dialog.destroy()
