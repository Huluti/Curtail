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

from .preferences import ImCompressorPrefsWindow
from .compressor import Compressor
from .tools import message_dialog, parse_filename, add_filechooser_filters, \
                    sizeof_fmt

UI_PATH = '/com/github/huluti/ImCompressor/ui/'
SETTINGS_SCHEMA = 'com.github.huluti.ImCompressor'


@Gtk.Template(resource_path=UI_PATH + 'window.ui')
class ImCompressorWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'ImCompressorWindow'

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)
    settings = Gtk.Settings.get_default()

    prefs_window = None

    headerbar = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    forward_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    mainbox = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    treeview_box = Gtk.Template.Child()
    treeview_scrolled_window = Gtk.Template.Child()
    treeview = Gtk.Template.Child()
    save_info_label = Gtk.Template.Child()
    filechooser_button = Gtk.Template.Child()
    toggle_lossy = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = kwargs['application']

        self.build_ui()
        self.create_actions()
        self.show_treeview(False)
        self.forward_button.set_sensitive(False)

    def build_ui(self):
        # Dark theme at start
        if self._settings.get_boolean('dark-theme'):
            self.toggle_dark_theme(True)

        # Headerbar
        builder = Gtk.Builder.new_from_resource(UI_PATH + 'menu.ui')
        window_menu = builder.get_object('window-menu')
        self.menu_button.set_menu_model(window_menu)

        # Mainbox - drag&drop
        enforce_target = Gtk.TargetEntry.new('text/plain',
                                             Gtk.TargetFlags(4), 0)
        self.mainbox.drag_dest_set(Gtk.DestDefaults.ALL, [enforce_target],
                                   Gdk.DragAction.COPY)
        self.mainbox.connect('drag-data-received', self.on_receive)

        # Treeview
        self.store = Gtk.ListStore(bool, str, str, str, str)
        self.treeview.set_model(self.store)
        self.renderer = Gtk.CellRendererText()

        spinner_renderer = Gtk.CellRendererSpinner.new()
        col_bool = Gtk.TreeViewColumn('', spinner_renderer, active=0)
        self.treeview.append_column(col_bool)
        self.add_column_to_treeview(_("Filename"), 1)
        self.add_column_to_treeview(_("Old Size"), 2)
        self.add_column_to_treeview(_("New Size"), 3)
        self.add_column_to_treeview(_("Savings"), 4)

        self.adjustment = self.treeview_scrolled_window.get_vadjustment()

        # Lossy toggle
        self.toggle_lossy.set_active(self._settings.get_boolean('lossy'))
        self.toggle_lossy.connect('notify::active', self.on_lossy_changed)

        # Info label
        self.change_save_info_label()

    def add_column_to_treeview(self, title, column_id):
        treeviewcolumn = Gtk.TreeViewColumn(title)
        if column_id in (0, 3):
            treeviewcolumn.set_sort_column_id(column_id)
        treeviewcolumn.set_spacing(10)
        treeviewcolumn.set_resizable(True)
        treeviewcolumn.set_expand(True)
        treeviewcolumn.pack_start(self.renderer, False)
        treeviewcolumn.add_attribute(self.renderer, 'text', column_id)
        self.treeview.append_column(treeviewcolumn)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.add_accelerator(shortcut, 'win.' + action_name, None)

    def create_actions(self):
        self.create_simple_action('back', self.on_back)
        self.create_simple_action('forward', self.on_forward)
        self.create_simple_action('select-file', self.on_select, '<Primary>o')
        self.create_simple_action('preferences', self.on_preferences)
        self.create_simple_action('about', self.on_about)
        self.create_simple_action('quit', self.on_quit, '<Primary>q')

    def show_treeview(self, show):
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

    def create_treeview_row(self, spinner, name, size):
        tree_iter = self.store.append([spinner, name, sizeof_fmt(size), '', ''])
        return tree_iter

    def update_treeview_row(self, tree_iter, new_size, savings):
        self.store.set_value(tree_iter, 3, sizeof_fmt(new_size))
        self.store.set_value(tree_iter, 4, '{}%'.format(str(savings)))

    def go_end_treeview(self):
        self.adjustment.set_value(self.adjustment.get_upper())

    def change_save_info_label(self):
        label = '<span size="small">{}</span>'
        if self._settings.get_boolean('new-file'):
            label = label.format(_("Images are saved with <b>'{}' suffix</b>.")\
                                 .format(self._settings.get_string('suffix')))
        else:
            label = label.format(_("Images are <b>overwritten</b>."))
        self.save_info_label.set_markup(label)

    def on_back(self, *args):
        self.show_treeview(False)

    def on_forward(self, *args):
        self.show_treeview(True)

    def on_select(self, *args):
        dialog = Gtk.FileChooserDialog(_("Browse your files"), self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_select_multiple(True)
        add_filechooser_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()  # we may have several files
        else:
            filenames = None
        dialog.destroy()

        if filenames:
           self.handle_filenames(filenames)

    def on_receive(self, widget, drag_context, x, y, data, info, time):
        filenames = data.get_text()
        filenames = filenames.split()  # we may have several paths
        self.handle_filenames(filenames)

    def handle_filenames(self, filenames):
        if not filenames:
            return
        final_filenames = []
        # Clean filenames
        for filename in filenames:
            filename = self.clean_filename(filename)
            to_add = self.check_filename(filename)
            if to_add:
                final_filenames.append(filename)
        # Do operations
        for filename in final_filenames:
            new_filename = self.create_new_filename(filename)
            self.compress_image(filename, new_filename)
            while Gtk.events_pending():
                Gtk.main_iteration()

    def clean_filename(self, filename):
        if filename.startswith('file://'):  # drag&drop
            filename = filename[7:]  # remove 'file://'
            filename = unquote(filename)  # remove %20
            filename = filename.strip('\r\n\x00')  # remove spaces
        return filename

    def check_filename(self, filename):
        if not path.exists(filename):  # if path doesn't exist
            message_dialog(self, 'error', _("Path not valid"),
                           _("\"{}\" doesn't exist.") \
                           .format(filename))
            return False

        if not path.isfile(filename):  # don't allow folders for now
            message_dialog(self, 'error', _("Operation not supported"),
                           _("Discovery of images in folders is not yet supported."))
            return False

        file_data = parse_filename(filename)

        if file_data['ext'] not in ('png', 'jpg', 'jpeg'):
            message_dialog(self, 'error', _("Format not supported"),
                        _("The format of \"{}\" is not supported.") \
                        .format(file_data['full_name']))
            return False
        return True

    def create_new_filename(self, filename):
        file_data = parse_filename(filename)
        # Use new file or not
        if self._settings.get_boolean('new-file'):
            new_filename = '{}/{}{}.{}'.format(file_data['folder'],
                file_data['name'], self._settings.get_string('suffix'),
                file_data['ext'])
        else :
            new_filename = filename
        return new_filename

    def compress_image(self, filename, new_filename):
        # Show tree view if hidden
        if not self.treeview_box.get_visible():
            self.show_treeview(True)
        # Call compressor
        compressor = Compressor(self, filename, new_filename)
        compressor.compress_image()
        self.go_end_treeview()  # scroll to enf of treeview

    def toggle_dark_theme(self, value):
        self.settings.set_property('gtk-application-prefer-dark-theme',
                                       value)

    def on_lossy_changed(self, switch, state):
        self._settings.set_boolean('lossy', switch.get_active())

    def on_preferences(self, *args):
        if self.prefs_window is not None:
            self.prefs_window.destroy()
        self.prefs_window = ImCompressorPrefsWindow(self)
        self.prefs_window.present()

    def on_about(self, *args):
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_logo_icon_name('com.github.huluti.ImCompressor')
        dialog.set_program_name('ImCompressor')
        dialog.set_version('0.6')
        dialog.set_website('https://github.com/Huluti/ImCompressor')
        dialog.set_authors(['Hugo Posnic'])
        dialog.set_translator_credits(_("translator-credits"))
        dialog.set_comments(_("Simple & useful image compressor"))
        text = _("Distributed under the GNU GPL(v3) license.\n")
        text += 'https://github.com/Huluti/ImCompressor/blob/master/COPYING\n'
        dialog.set_license(text)
        dialog.run()
        dialog.destroy()

    def on_quit(self, *args):
        self.app.quit()
