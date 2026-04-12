from gi.repository import Gio, GObject


class ResultItem(GObject.Object):
    file = GObject.Property(type=Gio.File)
    mime_type = GObject.Property(type=str)
    name = GObject.Property(type=str)
    filename = GObject.Property(type=str)
    new_filename = GObject.Property(type=str)
    tmp_filename = GObject.Property(type=str)
    size = GObject.Property(type=int, default=0)
    new_size = GObject.Property(type=int, default=0)
    subtitle_label = GObject.Property(type=str, default="")
    savings = GObject.Property(type=str, default="")
    running = GObject.Property(type=bool, default=True)
    skipped = GObject.Property(type=bool, default=False)
    error = GObject.Property(type=bool, default=False)
    error_message = GObject.Property(type=str, default="")
    error_details = GObject.Property(type=bool, default=False)
    error_details_message = GObject.Property(type=str, default="")

    def __repr__(self):
        return str(self.name)

    def set_error(self, error: str) -> None:
        self.error = True
        self.error_message = error
