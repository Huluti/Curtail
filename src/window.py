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

import os
import subprocess
from gi.repository import Gtk, Gdk, Gio, GLib, Adw, GObject
from urllib.parse import unquote
from pathlib import Path

from .resultitem import ResultItem
from .preferences import CurtailPrefsDialog
from .compressor import Compressor
from .tools import add_filechooser_filters, get_file_type, \
    create_image_from_file, sizeof_fmt, debug_infos, \
    get_image_files_from_folder, get_image_files_from_folder_recursive

CURTAIL_PATH = '/com/github/huluti/Curtail/'
SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


@Gtk.Template(resource_path=CURTAIL_PATH + 'ui/window.ui')
class CurtailWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CurtailWindow'

    _settings = Gio.Settings.new(SETTINGS_SCHEMA)
    settings = Gtk.Settings.get_default()

    prefs_dialog = None
    apply_window = None

    headerbar = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    filechooser_button_headerbar = Gtk.Template.Child()
    clear_button_headerbar = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    warning_banner = Gtk.Template.Child()
    mainbox = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    resultbox = Gtk.Template.Child()
    scrolled_window = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    toggle_lossy = Gtk.Template.Child()

    results_model = Gio.ListStore.new(ResultItem)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_icon_name('com.github.huluti.Curtail')
        self.app = kwargs['application']

        self.build_ui()
        self.create_actions()
        self.show_results(False)

    def build_ui(self):
        # Set icons
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_resource_path(CURTAIL_PATH + 'icons/')

        # Headerbar
        builder = Gtk.Builder.new_from_resource(CURTAIL_PATH + 'ui/menu.ui')
        window_menu = builder.get_object('window-menu')
        self.menu_button.set_menu_model(window_menu)

        # Saving subtitle
        self.set_saving_subtitle()

        # Warning banner
        self.show_warning_banner()

        # Mainbox - drag&drop
        drop_target_main = Gtk.DropTarget.new(type=Gdk.FileList, actions=Gdk.DragAction.COPY)
        drop_target_main.connect('drop', self.on_dnd_drop)
        self.mainbox.add_controller(drop_target_main)

        # Lossy toggle
        self.toggle_lossy.set_active(self._settings.get_boolean('lossy'))
        self.toggle_lossy.connect('notify::active', self.on_lossy_changed)

        # Results
        self.listbox.bind_model(self.results_model, self.create_result_row)

        # Right click on results
        gesture = Gtk.GestureClick.new()
        gesture.set_button(Gdk.BUTTON_SECONDARY)
        gesture.connect("pressed", self.on_results_right_click, self.listbox)
        self.listbox.add_controller(gesture)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.set_accels_for_action('win.' + action_name, [shortcut])

    def create_actions(self):
        self.create_simple_action('select-file', self.on_select, '<Primary>o')
        self.create_simple_action('clear-results', self.clear_results)
        self.create_simple_action('banner-change-mode', self.banner_change_mode)
        self.create_simple_action('preferences', self.on_preferences, '<Primary>comma')
        self.create_simple_action('about', self.on_about)
        self.create_simple_action('quit', self.on_quit, '<Primary>q')
        self.create_simple_action('convert-dir', self.on_select_folder, '<Primary>d')

    def enable_compression(self, enable):
        self.filechooser_button_headerbar.set_sensitive(enable)
        self.clear_button_headerbar.set_sensitive(enable)

    def show_results(self, show):
        if show:
            self.homebox.set_visible(False)
            self.resultbox.set_visible(True)
            self.clear_button_headerbar.set_visible(True)
        else:
            self.resultbox.set_visible(False)
            self.homebox.set_visible(True)
            self.clear_button_headerbar.set_visible(False)

    def clear_results(self, *args):
        self.show_results(False)
        self.results_model.remove_all()

    def update_result_item(self, result_item, error, error_message):
        result_item.running = False
        result_item.error = error
        if error:
            result_item.subtitle_label = error_message
        elif result_item.skipped:
            result_item.savings = _("Skipped")
        else:
            result_item.savings = str(round(100 - (result_item.new_size * 100 / result_item.size), 2)) + '%'
            result_item.subtitle_label += ' → ' + sizeof_fmt(result_item.new_size)

    def create_result_row(self, result_item):
        row = Adw.ActionRow()
        row.set_title(result_item.name)
        row.set_tooltip_text(result_item.new_filename)
        row.set_subtitle(result_item.subtitle_label)

        if len(result_item.new_filename) > 0:
            image = create_image_from_file(result_item.filename, 48, 48)
            if image:
                row.add_prefix(image)

        skipped_info_button = Gtk.MenuButton()
        skipped_info_button.set_valign(Gtk.Align.CENTER)
        skipped_info_button.set_tooltip_text(_("More Information"))
        skipped_info_button.set_icon_name("info-outline-symbolic")
        skipped_info_button.add_css_class("flat")
        skipped_info_button.set_visible(False)

        popover = Gtk.Popover()
        popover_label = Gtk.Label()
        popover_label.set_text(_("Compression was skipped because compressing the file would have resulted in a larger file size."))
        popover_label.set_halign(Gtk.Align.CENTER)
        popover_label.set_valign(Gtk.Align.CENTER)
        popover_label.set_margin_bottom(6)
        popover_label.set_margin_start(6)
        popover_label.set_margin_end(6)
        popover_label.set_margin_top(6)
        popover_label.set_max_width_chars(50)
        popover_label.set_wrap(True)
        popover.set_child(popover_label)

        skipped_info_button.set_popover(popover)
        row.add_suffix(skipped_info_button)

        savings_widget = Gtk.Label()
        savings_widget.add_css_class('success')
        row.add_suffix(savings_widget)

        spinner = Adw.Spinner()
        row.add_suffix(spinner)

        error_image = Gtk.Image.new_from_icon_name('x-circular-symbolic')
        error_image.set_visible(False)
        error_image.add_css_class('error')
        row.add_suffix(error_image)

        result_item.bind_property('savings', savings_widget, 'label',
            GObject.BindingFlags.DEFAULT)
        result_item.bind_property('subtitle_label', row, 'subtitle',
            GObject.BindingFlags.DEFAULT)
        result_item.bind_property('running', spinner, 'visible',
            GObject.BindingFlags.DEFAULT)
        result_item.bind_property('skipped', skipped_info_button, 'visible',
            GObject.BindingFlags.DEFAULT)
        result_item.bind_property('error', error_image, 'visible',
            GObject.BindingFlags.DEFAULT)

        return row

    def on_results_right_click(self, gesture, button, x, y, user_data):
        row = self.listbox.get_row_at_y(y)
        filename = row.get_tooltip_text()
        if not os.path.exists(filename):
            return

        popover = Gtk.PopoverMenu()

        # Create actions for the popover
        action_group = Gio.SimpleActionGroup.new()

        open_image_action = Gio.SimpleAction.new("open-image", None)
        open_image_action.connect("activate", self.on_open_image_action, filename)
        action_group.add_action(open_image_action)

        open_folder_action = Gio.SimpleAction.new("open-folder", None)
        open_folder_action.connect("activate", self.on_open_folder_action, filename)
        action_group.add_action(open_folder_action)

        # Insert the actions into the window's action group
        self.insert_action_group("context-menu", action_group)

        # Define the structure of the popover menu
        menu_model = Gio.Menu.new()
        menu_model.append(_("Open Image"), "context-menu.open-image")
        menu_model.append(_("Show in Folder"), "context-menu.open-folder")

        # Set the menu model to the popover
        popover.set_menu_model(menu_model)
        popover.set_pointing_to(Gdk.Rectangle(x, y, 1, 1))
        popover.set_offset(x, y)
        popover.set_has_arrow(False)
        popover.set_parent(self.listbox)
        popover.popup()

    def on_open_image_action(self, action, param, filename):
        subprocess.run(['xdg-open', filename])

    def on_open_folder_action(self, action, param, filename):
        folder_path = os.path.dirname(filename)
        subprocess.run(['xdg-open', folder_path])

    def set_saving_subtitle(self, new_file=None):
        if new_file is None:
            new_file = self._settings.get_boolean('new-file')
        if new_file:
            label = _("Safe mode with '{}' suffix")\
                                 .format(self._settings.get_string('suffix'))
        else:
            label = _("Overwrite mode")
        self.window_title.set_subtitle(label)

    def show_warning_banner(self, show=None):
        if show is None:
            show = not self._settings.get_boolean('new-file')

        self.warning_banner.set_revealed(show)

    def on_select(self, *args):
        dialog = Gtk.FileDialog(title=_("Browse Files"))
        add_filechooser_filters(dialog)

        def handle_response(dialog, result):
            try:
                files = dialog.open_multiple_finish(result)
            except GLib.Error as err:
                print("Could not open files: %s", err.message)
            else:
                filenames = list()
                for file in files:
                    filenames.append(file.get_uri())
                self.compress_filenames(filenames)

        dialog.open_multiple(self, None, handle_response)

    def on_select_folder(self, *args):
        dialog = Gtk.FileDialog(title=_("Browse Directories"))

        def handle_response(dialog, result):
            def on_dir_dialog_response(warn_dialog, response):
                if response == "compress":
                    filenames = list()
                    for folder in folders:
                        filenames.append(folder.get_path())
                    self.compress_filenames(filenames)

            try:
                folders = dialog.select_multiple_folders_finish(result)
            except GLib.Error as err:
                print("Could not open files: %s", err.message)
            else:
                warning_message_dialog = self._create_warning_dialog()
                warning_message_dialog.connect("response", on_dir_dialog_response)
                warning_message_dialog.present(self)

        dialog.select_multiple_folders(self, None, handle_response)

    def _create_warning_dialog(self):
        dialog = None
        if self._settings.get_boolean('new-file'):
            dialog = Adw.AlertDialog.new(
                _("Are you sure you want to compress images in these directories?"),
                _("All of the images in the directories selected and their "
                "subdirectories will be compressed. The original images will not "
                "be modified."))
        else:
            dialog = Adw.AlertDialog.new(
                _("Are you sure you want to compress images in these directories?"),
                _("All of the images in the directories selected and their "
                "subdirectories will be compressed and overwritten!"))

        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("compress", _("Compress"))

        if self._settings.get_boolean('new-file'):
            dialog.set_response_appearance("compress", Adw.ResponseAppearance.SUGGESTED)
        else:
            dialog.set_response_appearance("compress", Adw.ResponseAppearance.DESTRUCTIVE)

        return dialog

    def on_dnd_drop(self, drop_target, value, x, y, user_data=None):
        files = value.get_files()
        if not files:
            return

        filenames = []
        for file in files:
            filenames.append(file.get_uri())
        self.compress_filenames(filenames)

    def handle_filenames(self, filenames):
        final_filenames = []
        # Clean filenames
        for filename in filenames:
            filename = self.clean_filename(filename)

            path = Path(filename)
            if path.is_dir():
                if self._settings.get_boolean('recursive'):
                    images = get_image_files_from_folder_recursive(path)
                else:
                    images = get_image_files_from_folder(path)
                for image in images:
                    image = self.clean_filename(image)
                    final_filenames.append(image)
            else:
                final_filenames.append(filename)

        return final_filenames

    def clean_filename(self, filename):
        filename = str(filename)
        if filename.startswith('file://'):  # drag&drop
            filename = filename[7:]  # remove 'file://'
            filename = unquote(filename)  # remove %20
            filename = filename.strip('\r\n\x00')  # remove spaces
        return filename

    def check_format(self, filename):
        file_type = get_file_type(filename)
        if file_type:
            return file_type in ('png', 'jpg', 'webp', 'svg')
        else:
            return False

    def create_new_filename(self, path):
        # Use new file or not
        if self._settings.get_boolean('new-file'):
            new_filename = '{}/{}{}{}'.format(path.parents[0],
                path.stem, self._settings.get_string('suffix'),
                path.suffix)
        else :
            new_filename = str(path)
        return new_filename

    def compress_filenames(self, filenames):
        filenames = self.handle_filenames(filenames)

        # No files found
        if not filenames:
            self.toast_overlay.add_toast(Adw.Toast(title=_("No files found")))
            return

        result_items = []
        for filename in filenames:
            error_message = False
            path = Path(filename)

            # Check file
            if not path.is_file():
                error_message = _("This file doesn't exist.").format(filename)

            # Check format
            size = path.stat().st_size
            if not self.check_format(filename) or size <= 0:
                error_message = _("Format of this file is not supported.").format(path.name)

            if not error_message:
                new_filename = self.create_new_filename(path)
            else:
                new_filename = ''

            result_item = ResultItem(path.name, filename, new_filename, size)

            if not error_message:
                result_items.append(result_item)

            self.results_model.append(result_item)

            if error_message:
                GLib.idle_add(self.update_result_item, result_item, True, error_message)

        self.compress_images(result_items)

    def compress_images(self, result_items):
        self.show_results(True)
        self.enable_compression(False)

        compressor = Compressor(result_items, self.update_result_item, self.enable_compression)
        GLib.idle_add(compressor.compress_images)

    def on_lossy_changed(self, switch, state):
        self._settings.set_boolean('lossy', switch.get_active())

    def banner_change_mode(self, *args):
        self._settings.set_boolean('new-file', True)
        self.show_warning_banner()
        self.set_saving_subtitle()

    def on_preferences(self, *args):
        if self.prefs_dialog is not None:
            self.prefs_dialog.force_close()
        self.prefs_dialog = CurtailPrefsDialog(self)
        self.prefs_dialog.present(self)

    def on_about(self, *args):
        about = Adw.AboutDialog(
                    application_name='Curtail',
                    application_icon='com.github.huluti.Curtail',
                    developer_name='Hugo Posnic',
                    license_type=Gtk.License.GPL_3_0,
                    website='https://github.com/Huluti/Curtail',
                    issue_url='https://github.com/Huluti/Curtail/issues/new',
                    version='1.11.1',
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
            _('Contributors'),
            [
                'Steven Teskey',
                'Andrey Kozlovskiy',
                'Balló György',
                'olokelo',
                'Archisman Panigrahi',
                'Maximiliano',
                'ARAKHNID'
            ]
        )
        about.set_debug_info(debug_infos())
        about.present(self)

    def on_quit(self, *args):
        self.app.quit()

