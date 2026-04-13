import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, Adw  # noqa: E402

from .window import CurtailWindow  # noqa: E402


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
        self.win.compress_files(g_file_list)


def main(version):
    app = Application(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_OPEN)
    return app.run(sys.argv)
