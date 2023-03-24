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
from gi.repository import Gtk, Gdk, Gio, GLib, Adw
from urllib.parse import unquote
from pathlib import Path

from .preferences import CurtailPrefsWindow
from .compressor import Compressor
from .tools import message_dialog, add_filechooser_filters, \
                    sizeof_fmt, get_file_type, create_image_from_file

UI_PATH = '/com/github/huluti/Curtail/ui/'
SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


@Gtk.Template(resource_path=UI_PATH + 'window.ui')
class CurtailWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CurtailWindow'

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)
    settings = Gtk.Settings.get_default()

    prefs_window = None
    apply_window = None

    headerbar = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    forward_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    mainbox = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    resultbox = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    save_info_label = Gtk.Template.Child()
    filechooser_button = Gtk.Template.Child()
    toggle_lossy = Gtk.Template.Child()

    apply_to_queue = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_icon_name('com.github.huluti.Curtail')
        self.app = kwargs['application']

        self.build_ui()
        self.create_actions()
        self.show_results(False)
        self.forward_button.set_sensitive(False)

    def build_ui(self):
        # Headerbar
        builder = Gtk.Builder.new_from_resource(UI_PATH + 'menu.ui')
        window_menu = builder.get_object('window-menu')
        self.menu_button.set_menu_model(window_menu)

        # Mainbox - drag&drop
        drop_target_main = Gtk.DropTarget.new(type=Gdk.FileList, actions=Gdk.DragAction.COPY)
        drop_target_main.connect('drop', self.on_dnd_drop)
        self.mainbox.add_controller(drop_target_main)

        # Lossy toggle
        self.toggle_lossy.set_active(self._settings.get_boolean('lossy'))
        self.toggle_lossy.connect('notify::active', self.on_lossy_changed)

        # Info label
        self.change_save_info_label()

        # Results
        self.adjustment = self.scrolled_window.get_vadjustment()

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.set_accels_for_action('win.' + action_name, [shortcut])

    def create_actions(self):
        self.create_simple_action('back', self.on_back)
        self.create_simple_action('forward', self.on_forward)
        self.create_simple_action('select-file', self.on_select, '<Primary>o')
        self.create_simple_action('preferences', self.on_preferences, '<Primary>comma')
        self.create_simple_action('about', self.on_about)
        self.create_simple_action('quit', self.on_quit, '<Primary>q')

    def show_results(self, show):
        if show:
            self.homebox.set_visible(False)
            self.resultbox.set_visible(True)
        else:
            self.resultbox.set_visible(False)
            self.homebox.set_visible(True)
        self.back_button.set_sensitive(show)
        self.forward_button.set_sensitive(not show)
        self.sync_ui()

    def go_end_scrolledwindow(self):
        self.adjustment.set_value(self.adjustment.get_upper())

    def sync_ui(self):
        main_context = GLib.MainContext.default()
        while main_context.pending():
            main_context.iteration(False)

    def create_result_row(self, name, filename, new_filename, size):
        row = Adw.ActionRow()
        row.set_title(name)
        row.set_tooltip_text(new_filename)
        subtitle = sizeof_fmt(size)
        row.set_subtitle(subtitle)

        image = create_image_from_file(filename, 60, 60)
        row.add_prefix(image)

        self.listbox.insert(row, -1)  # insert at end

        self.sync_ui()

        return row

    def update_result_row(self, row, size, new_size, savings):
        subtitle = sizeof_fmt(size) + ' -> ' + sizeof_fmt(new_size)
        row.set_subtitle(subtitle)

        savings_widget = Gtk.Label(label=str(savings) + '%')
        color = 'success' if savings > 0 else 'error'
        savings_widget.add_css_class(color)
        row.add_suffix(savings_widget)

        self.sync_ui()

    def change_save_info_label(self):
        label = '<span size="small">{}</span>'
        if self._settings.get_boolean('new-file'):
            label = label.format(_("Images are saved with <b>'{}' suffix</b>.")\
                                 .format(self._settings.get_string('suffix')))
        else:
            label = label.format(_("Images are <b>overwritten</b>."))
        self.save_info_label.set_markup(label)

    def on_back(self, *args):
        self.show_results(False)

    def on_forward(self, *args):
        self.show_results(True)

    def on_select(self, *args):
        dialog = Gtk.FileDialog(title=_("Browse Files"))
        add_filechooser_filters(dialog)

        def handle_response(dialog, result):
            files = dialog.open_multiple_finish(result)
            filenames = list()
            for file in files:
                filenames.append(file.get_uri())
            final_filenames = self.handle_filenames(filenames)
            self.compress_filenames(final_filenames)

        dialog.open_multiple(self, None, handle_response)

    def on_dnd_drop(self, drop_target, value, x, y, user_data=None):
        files = value.get_files()
        if not files:
            return

        filenames = []
        for file in files:
            filenames.append(file.get_uri())

        final_filenames = self.handle_filenames(filenames)
        self.compress_filenames(final_filenames)

    def handle_filenames(self, filenames):
        final_filenames = []
        # Clean filenames
        for filename in filenames:
            filename = self.clean_filename(filename)
            verified_filenames = self.check_filename(filename)
            final_filenames = final_filenames + verified_filenames
        return final_filenames

    def clean_filename(self, filename):
        if filename.startswith('file://'):  # drag&drop
            filename = filename[7:]  # remove 'file://'
            filename = unquote(filename)  # remove %20
            filename = filename.strip('\r\n\x00')  # remove spaces
        return filename

    def check_extension(self, filename):
        file_type = get_file_type(filename)
        if file_type:
            return file_type in ('png', 'jpg', 'webp')
        else:
            return False

    def check_filename(self, filename):
        verified_filenames = []

        path = Path(filename)

        if Path.is_dir(path):
            for new_filename in path.rglob("*"):
                new_path = Path(new_filename)
                if Path.is_file(new_path):
                    if self.check_extension(new_path):
                        verified_filenames.append(new_filename)
        elif Path.is_file(path):
            size = path.stat().st_size
            if not self.check_extension(filename) or size <= 0:
                message_dialog(self, _("Format not supported"),
                    _("The format of {} is not supported.").format(path.name))
            else:
                verified_filenames.append(filename)
        else:
            message_dialog(self, _("Path not valid"),
                           _("{} doesn't exist.").format(filename))

        return verified_filenames

    def create_new_filename(self, filename):
        path = Path(filename)

        # Use new file or not
        if self._settings.get_boolean('new-file'):
            new_filename = '{}/{}{}{}'.format(path.parents[0],
                path.stem, self._settings.get_string('suffix'),
                path.suffix)
        else :
            new_filename = filename
        return new_filename

    def compress_filenames(self, filenames):
        # Do operations
        files = []
        needs_overwrite = False
        for filename in filenames:
            new_filename = self.create_new_filename(filename)
            files.append({'filename': filename, 'new_filename': new_filename})

            new_file_data = Path(new_filename)
            if not needs_overwrite and new_file_data.is_file():  # verify if new file path exists
                needs_overwrite = True

        if (needs_overwrite):
            dialog = Adw.MessageDialog.new(
                self,
                _('Some files already exists'),
                _('If you continue, some files will be overwritten.')
            )
            dialog.add_response(Gtk.ResponseType.CANCEL.value_nick, _("_Cancel"))
            dialog.add_response(Gtk.ResponseType.OK.value_nick, _("C_onfirm"))
            dialog.set_response_appearance(
                response=Gtk.ResponseType.OK.value_nick,
                appearance=Adw.ResponseAppearance.DESTRUCTIVE
            )

            def handle_response(_dialog, response: Gtk.ResponseType):
                if response == Gtk.ResponseType.OK.value_nick:
                    self.compress_images(files)

                dialog.close()

            dialog.connect('response', handle_response)
            dialog.present()
        else:
            self.compress_images(files)

    def compress_images(self, files):
        self.show_results(True)

        for file in files:
            # Call compressor
            compressor = Compressor(self, file['filename'],
                file['new_filename'])
            compressor.compress_image()
            self.go_end_scrolledwindow()

    def on_lossy_changed(self, switch, state):
        self._settings.set_boolean('lossy', switch.get_active())

    def on_preferences(self, *args):
        if self.prefs_window is not None:
            self.prefs_window.destroy()
        self.prefs_window = CurtailPrefsWindow(self)
        self.prefs_window.present()

    def on_about(self, *args):
        about = Adw.AboutWindow(
                    transient_for=self,
                    application_name='Curtail',
                    application_icon='com.github.huluti.Curtail',
                    developer_name='Hugo Posnic',
                    license_type=Gtk.License.GPL_3_0,
                    website='https://github.com/Huluti/Curtail',
                    issue_url='https://github.com/Huluti/Curtail/issues/new',
                    version='1.5.0',
                    developers=[
                        'Hugo Posnic https://github.com/Huluti'
                    ],
                    designers=[
                        'Jakub Steiner https://github.com/jimmac',
                        'Tobias Bernard https://github.com/bertob'
                    ],
                    translator_credits=_("translator-credits"),
                    copyright='© Hugo Posnic'
                )
        about.add_credit_section(
            _("Contributors"),
            [
                'Steven Teskey',
                'Andrey Kozlovskiy',
                'Balló György',
                'olokelo',
                'Archisman Panigrahi',
                'Maximiliano'
            ]
        )
        about.present()

    def on_quit(self, *args):
        self.app.quit()
