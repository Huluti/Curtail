# resultitem.py

from gi.repository import GObject

class ResultItem(GObject.Object):
    name = GObject.Property(type=str)
    filename = GObject.Property(type=str)
    new_filename = GObject.Property(type=str)
    size = GObject.Property(type=str)
    savings = GObject.Property(type=str)

    def __init__(self, name, filename, new_filename, size, savings):
        super().__init__()

        self.name = name
        self.filename = filename
        self.new_filename = new_filename
        self.size = size
        self.savings = savings

    def __repr__(self):
        return str(self.name)
