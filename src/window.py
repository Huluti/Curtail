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
    back_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    treeview = Gtk.Template.Child()
    filechooser_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.build_ui()
        self.create_actions()
        self.show_treeview(False)

    def build_ui(self):
        # Headerbar
        builder = Gtk.Builder.new_from_resource(UI_PATH + 'menu.ui')
        window_menu = builder.get_object('window-menu')
        self.menu_button.set_menu_model(window_menu)

        # Treeview
        self.store = Gtk.ListStore(str)
        self.treeview.set_model(self.store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Filename"), renderer, text=0)
        self.treeview.append_column(column)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.add_accelerator(shortcut, 'win.' + action_name, None)

    def create_actions(self):
        self.create_simple_action('back', self.back)
        self.create_simple_action('select_file', self.select_file)
        self.create_simple_action('about', self.about_window)

    def show_treeview(self, show=True):
        if show:
            self.homebox.hide()
            self.treeview.show_all()
        else:
            self.treeview.hide()
            self.homebox.show_all()
        self.back_button.set_sensitive(show)

    def back(self, *args):
        self.show_treeview(False)

    def select_file(self, *args):
        file_chooser = Gtk.FileChooserNative()
        file_chooser.set_transient_for(self)
        file_chooser.set_action(Gtk.FileChooserAction.OPEN)
        self.add_filechooser_filters(file_chooser)

        response = file_chooser.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = file_chooser.get_filename()
            self.compress_image(filename)
        file_chooser.destroy()
        return None

    def compress_image(self, filename):
        self.show_treeview(True)

        treeiter = self.store.append([filename])

    def add_filechooser_filters(self, filechooser_filters):
        all_images = Gtk.FileFilter()
        all_images.set_name(_("All images"))
        all_images.add_mime_type('image/jpeg')
        all_images.add_mime_type('image/png')

        png_images = Gtk.FileFilter()
        png_images.set_name(_("PNG images"))
        png_images.add_mime_type('image/png')

        jpeg_images = Gtk.FileFilter()
        jpeg_images.set_name(_("JPEG images"))
        jpeg_images.add_mime_type('image/jpeg')

        filechooser_filters.add_filter(all_images)
        filechooser_filters.add_filter(png_images)
        filechooser_filters.add_filter(jpeg_images)

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
