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

import subprocess
from gi.repository import Gtk, Gdk, Gio
from urllib.parse import unquote
from os import path

from .compressor import Compressor
from .tools import message_dialog


UI_PATH = '/com/github/ImCompressor/ui/'


@Gtk.Template(resource_path=UI_PATH + 'window.ui')
class ImCompressorWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'ImCompressorWindow'

    headerbar = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    forward_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    mainbox = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    treeview_box = Gtk.Template.Child()
    treeview = Gtk.Template.Child()
    filechooser_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = kwargs['application']

        self.build_ui()
        self.create_actions()
        self.show_treeview(False)
        self.forward_button.set_sensitive(False)

    def build_ui(self):
        # Headerbar
        builder = Gtk.Builder.new_from_resource(UI_PATH + 'menu.ui')
        window_menu = builder.get_object('window-menu')
        self.menu_button.set_menu_model(window_menu)

        # Mainbox - drag&drop
        enforce_target = Gtk.TargetEntry.new('text/plain',
                                             Gtk.TargetFlags(4), 0)
        self.mainbox.drag_dest_set(Gtk.DestDefaults.ALL, [enforce_target],
                                   Gdk.DragAction.COPY)
        self.mainbox.connect('drag-data-received', self.receive_file)

        # Treeview
        self.store = Gtk.ListStore(str, str, str, str)
        self.treeview.set_model(self.store)
        self.renderer = Gtk.CellRendererText()

        self.add_column_to_treeview(_("Filename"), 0)
        self.add_column_to_treeview(_("Size"), 1)
        self.add_column_to_treeview(_("New Size"), 2)
        self.add_column_to_treeview(_("Savings"), 3)

    def add_column_to_treeview(self, title, column_id):
        treeviewcolumn = Gtk.TreeViewColumn(title)
        treeviewcolumn.set_spacing(10)
        treeviewcolumn.set_resizable(True)
        treeviewcolumn.pack_start(self.renderer, False)
        treeviewcolumn.add_attribute(self.renderer, 'text', column_id)
        if column_id == 0:
            treeviewcolumn.set_expand(True)
        self.treeview.append_column(treeviewcolumn)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.add_accelerator(shortcut, 'win.' + action_name, None)

    def create_actions(self):
        self.create_simple_action('back', self.back)
        self.create_simple_action('forward', self.forward)
        self.create_simple_action('select_file', self.select_file)
        self.create_simple_action('about', self.about_window)
        self.create_simple_action('quit', self.quit_app, '<Primary>q')

    def show_treeview(self, show=True):
        if show:
            self.homebox.hide()
            self.treeview_box.show_all()
            self.back_button.set_sensitive(True)
            self.forward_button.set_sensitive(False)
        else:
            self.treeview_box.hide()
            self.homebox.show_all()
            self.back_button.set_sensitive(False)
            self.forward_button.set_sensitive(True)

    def back(self, *args):
        self.show_treeview(False)

    def forward(self, *args):
        self.show_treeview(True)

    def select_file(self, *args):
        dialog = Gtk.FileChooserDialog(_("Please choose file(s)"), self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_select_multiple(True)
        self.add_filechooser_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()  # we may have several files
        else:
            filenames = None
        dialog.destroy()

        if filenames:
            for filename in filenames:
                self.compress_image(filename)

    def receive_file(self, widget, drag_context, x, y, data, info, time):
        filenames = data.get_text()
        filenames = filenames.split()  # we may have several files
        for filename in filenames:
            if filename.startswith('file://'):
                filename = filename[7:]  # 7 is len('file://')
                filename = unquote(filename)  # remove %20
                filename = filename.strip('\r\n\x00')  # remove spaces
                self.compress_image(filename)

    def parse_filename(self, filename):
        parse_filename = path.split(filename)
        parse_name = parse_filename[1].split('.')
        pfilename = {
            'folder': parse_filename[0],
            'full_name': parse_filename[1],
            'name': parse_name[0],
            'ext': parse_name[1].lower()
        }
        return pfilename

    def check_filename(self, filename):
        if not path.exists(filename):  # if path doesn't exist
            message_dialog(self, 'error', _("Doesn't exist"),
                           _("This image doesn't exist."))
            return

        # New filename
        pfilename = self.parse_filename(filename)

        if pfilename['ext'] not in ('png', 'jpg', 'jpeg'):
            message_dialog(self, 'error', _("Format not supported"),
                           _("This format of image is not supported."))
            return

        new_filename = '{}/{}-min.{}'.format(pfilename['folder'],
            pfilename['name'], pfilename['ext'])

        if path.exists(new_filename):  # already minimized
            message_dialog(self, 'info', _("Already minimized"),
                           _("This image is already minimized."))
            return

        return filename, new_filename, pfilename

    def compress_image(self, filename):
        data = self.check_filename(filename)
        if data is not None:
            compressor = Compressor(self, data)
            compressor.start()
            compressor.join()

    def add_filechooser_filters(self, dialog):
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

        dialog.add_filter(all_images)
        dialog.add_filter(png_images)
        dialog.add_filter(jpeg_images)

    def about_window(self, *args):
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_logo_icon_name('com.github.ImCompressor')
        dialog.set_program_name('ImCompressor')
        dialog.set_version('0.1')
        dialog.set_website('https://github.com/Huluti/ImCompressor')
        dialog.set_authors(['Hugo Posnic'])
        dialog.set_comments(_("Simple & useful image compressor"))
        text = _("Distributed under the GNU GPL(v3) license.\n")
        text += 'https://github.com/Huluti/ImCompressor/blob/master/COPYING\n'
        dialog.set_license(text)
        dialog.run()
        dialog.destroy()

    def quit_app(self, *args):
        self.app.quit()
