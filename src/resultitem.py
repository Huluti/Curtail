# resultitem.py

from gi.repository import GObject

from .tools import sizeof_fmt


class ResultItem(GObject.Object):
    name = GObject.Property(type=str)
    filename = GObject.Property(type=str)
    new_filename = GObject.Property(type=str)
    original_filename = GObject.Property(type=str)
    size = GObject.Property(type=int)
    new_size = GObject.Property(type=int, default=0)
    subtitle_label = GObject.Property(type=str, default="")
    savings = GObject.Property(type=str, default="")
    running = GObject.Property(type=bool, default=True)
    skipped = GObject.Property(type=bool, default=False)
    error = GObject.Property(type=bool, default=False)
    error_message = GObject.Property(type=str, default="")

    def __init__(self, name, filename, new_filename, size):
        super().__init__()

        self.name = name
        self.filename = filename
        self.new_filename = new_filename
        self.original_filename = filename
        self.size = size
        self.subtitle_label = sizeof_fmt(size)

    def __repr__(self):
        return str(self.name)
