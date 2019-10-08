# main.py
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

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio

from .window import ImCompressorWindow


APP_ID = 'com.github.huluti.ImCompressor'


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.win = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.connect('open', self.file_open_handler)

    def do_activate(self):
        if not self.win:
            self.win = ImCompressorWindow(application=self)
        self.win.present()

    def file_open_handler(self, app, g_file_list, amount, ukwn):
        self.do_activate()
        for g_file in g_file_list:
            self.win.compress_image(filename=g_file.get_path())


def main(version):
    app = Application()
    return app.run(sys.argv)
