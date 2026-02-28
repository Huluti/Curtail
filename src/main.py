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

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, Adw  # noqa: E402

from .window import CurtailWindow # noqa: E402


APP_ID = "com.github.huluti.Curtail"


class Application(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win: CurtailWindow | None = None

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        if not self.win:
            self.win = CurtailWindow(application=self)
        self.win.present()

    def do_open(self, g_file_list, amount, ukwn):
        self.do_activate()
        filenames = []
        for g_file in g_file_list:
            filenames.append(g_file.get_uri())
        final_filenames = self.win.handle_filenames(filenames)
        self.win.compress_filenames(final_filenames)


def main(version):
    app = Application(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)
    return app.run(sys.argv)
