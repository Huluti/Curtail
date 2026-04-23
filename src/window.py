import os
import subprocess
from gi.repository import Gtk, Gdk, Gio, GLib, Adw, GObject

from .compressors.png_compressor import PNGCompressor
from .compressors.jpeg_compressor import JPEGCompressor
from .compressors.webp_compressor import WEBPCompressor
from .compressors.svg_compressor import SVGCompressor
from .compression_manager import CompressionManager
from .settings_manager import SettingsManager
from .result_item import ResultItem
from .result_item_manager import ResultItemManager
from .result_item_row import CurtailResultItemRow
from .preferences import CurtailPrefsDialog
from .tools import (
    add_filechooser_filters,
    sizeof_fmt,
    debug_infos,
    get_image_files_from_folder,
    get_image_files_from_folder_recursive,
)

CURTAIL_PATH = "/com/github/huluti/Curtail/"


@Gtk.Template(resource_path=CURTAIL_PATH + "ui/window.ui")
class CurtailWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CurtailWindow"

    prefs_dialog = None
    apply_window = None

    headerbar = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    filechooser_button_headerbar = Gtk.Template.Child()
    clear_button_headerbar = Gtk.Template.Child()
    warning_banner = Gtk.Template.Child()
    mainbox = Gtk.Template.Child()
    loadingbox = Gtk.Template.Child()
    homebox = Gtk.Template.Child()
    resultbox = Gtk.Template.Child()
    listbox = Gtk.Template.Child()
    toggle_lossy = Gtk.Template.Child()

    results_model = Gio.ListStore.new(ResultItem)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_icon_name("com.github.huluti.Curtail")
        self.app = kwargs["application"]

        self.settings = SettingsManager()

        self.build_ui()
        self.create_actions()
        self.show_view("home")

        self.manager = CompressionManager(self.settings)
        self.manager.register_compressor(PNGCompressor)
        self.manager.register_compressor(JPEGCompressor)
        self.manager.register_compressor(WEBPCompressor)
        self.manager.register_compressor(SVGCompressor)

        self.result_item_manager = ResultItemManager(self.settings)

    def build_ui(self):
        # Set icons
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_resource_path(CURTAIL_PATH + "icons/")

        # Saving subtitle
        self.set_saving_subtitle()

        # Warning banner
        self.show_warning_banner()

        # Mainbox - drag&drop
        drop_target_main = Gtk.DropTarget.new(
            type=Gdk.FileList, actions=Gdk.DragAction.COPY
        )
        drop_target_main.connect("drop", self.on_dnd_drop)
        self.mainbox.add_controller(drop_target_main)

        # Lossy toggle
        self.toggle_lossy.set_active(self.settings.lossy)
        self.toggle_lossy.connect("notify::active", self.on_lossy_changed)

        # Results
        self.listbox.bind_model(
                self.results_model, lambda result_item : CurtailResultItemRow(result_item)
        )

        # Right click on results
        gesture = Gtk.GestureClick.new()
        gesture.set_button(Gdk.BUTTON_SECONDARY)
        gesture.connect("pressed", self.on_results_right_click, self.listbox)
        self.listbox.add_controller(gesture)

    def create_simple_action(self, action_name, callback, shortcut=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcut is not None:
            self.app.set_accels_for_action("win." + action_name, [shortcut])

    def create_actions(self):
        self.create_simple_action("select-file", self.on_select, "<Primary>o")
        self.create_simple_action("clear-results", self.clear_results)
        self.create_simple_action("banner-change-mode", self.banner_change_mode)
        self.create_simple_action("preferences", self.on_preferences, "<Primary>comma")
        self.create_simple_action("about", self.on_about)
        self.create_simple_action("quit", self.on_quit, "<Primary>q")
        self.create_simple_action("convert-dir", self.on_select_folder, "<Primary>d")

    def enable_compression(self, enable):
        self.filechooser_button_headerbar.set_sensitive(enable)
        self.clear_button_headerbar.set_sensitive(enable)

    def show_view(self, view):
        if view == "home":
            self.homebox.set_visible(True)
            self.loadingbox.set_visible(False)
            self.resultbox.set_visible(False)
            self.clear_button_headerbar.set_visible(False)
        elif view == "loading":
            self.homebox.set_visible(False)
            self.loadingbox.set_visible(True)
            self.resultbox.set_visible(False)
            self.clear_button_headerbar.set_visible(False)
        elif view == "results":
            self.homebox.set_visible(False)
            self.loadingbox.set_visible(False)
            self.resultbox.set_visible(True)
            self.clear_button_headerbar.set_visible(True)

    def clear_results(self, *args):
        self.show_view("home")
        self.results_model.remove_all()

    def update_result_item(self, result_item):
        result_item.running = False
        if result_item.error:
            result_item.subtitle_label = result_item.error_message
        elif result_item.skipped:
            result_item.savings = _("Skipped")
        else:
            result_item.savings = (
                str(round(100 - (result_item.new_size * 100 / result_item.size), 2))
                + "%"
            )
            result_item.subtitle_label += " → " + sizeof_fmt(result_item.new_size)

    def on_results_right_click(self, gesture, button, x, y, user_data):
        row = self.listbox.get_row_at_y(y)
        filename = row.get_tooltip_text()
        if not filename or not os.path.exists(filename):
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
        subprocess.run(["xdg-open", filename])

    def on_open_folder_action(self, action, param, filename):
        folder_path = os.path.dirname(filename)
        subprocess.run(["xdg-open", folder_path])

    def set_saving_subtitle(self, new_file=None):
        if new_file is None:
            new_file = self.settings.new_file
        if new_file:
            suffix_prefix = self.settings.suffix_prefix

            if self.settings.naming_mode == 0:
                label = _(f"Safe mode with “{suffix_prefix}” suffix")
            else:
                label = _(f"Safe mode with “{suffix_prefix}” prefix")
        else:
            label = _("Overwrite mode")
        self.window_title.set_subtitle(label)

    def show_warning_banner(self, show=None):
        if show is None:
            show = not self.settings.new_file

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
                self.show_view("loading")
                filenames = list()
                for file in files:
                    filenames.append(file.get_uri())
                self.compress_files(files)

        dialog.open_multiple(self, None, handle_response)

    def on_select_folder(self, *args):
        dialog = Gtk.FileDialog(title=_("Browse Directories"))

        def handle_response(dialog, result):
            def on_dir_dialog_response(warn_dialog, response):
                if response == "compress":
                    self.show_view("loading")
                    filenames = list()
                    for folder in folders:
                        filenames.append(folder)
                    self.compress_files(filenames)

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
        if self.settings.new_file:
            dialog = Adw.AlertDialog.new(
                _("Are you sure you want to compress images in these directories?"),
                _(
                    "All of the images in the directories selected and their "
                    "subdirectories will be compressed. The original images will not "
                    "be modified."
                ),
            )
        else:
            dialog = Adw.AlertDialog.new(
                _("Are you sure you want to compress images in these directories?"),
                _(
                    "All of the images in the directories selected and their "
                    "subdirectories will be compressed and overwritten!"
                ),
            )

        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("compress", _("Compress"))

        if self.settings.new_file:
            dialog.set_response_appearance("compress", Adw.ResponseAppearance.SUGGESTED)
        else:
            dialog.set_response_appearance(
                "compress", Adw.ResponseAppearance.DESTRUCTIVE
            )

        return dialog

    def on_dnd_drop(self, drop_target, value, x, y, user_data=None):
        self.show_view("loading")
        files = value.get_files()
        if not files:
            return

        self.compress_files(files)

    def handle_files(self, files):
        final_files = []
        for file in files:
            file_type = file.query_file_type(Gio.FileQueryInfoFlags.NONE)

            if file_type == Gio.FileType.DIRECTORY:
                if self.settings.recursive:
                    images = get_image_files_from_folder_recursive(file)
                else:
                    images = get_image_files_from_folder(file)
                final_files.extend(images)
            else:
                final_files.append(file)

        return final_files

    def compress_files(self, files):
        files = self.handle_files(files)
        if not files:
            self.toast_overlay.add_toast(Adw.Toast(title=_("No files found")))
            return

        result_items = []
        for file in files:
            result_item = self.result_item_manager.build(file)
            self.results_model.append(result_item)

            if result_item.error:
                GLib.idle_add(self.update_result_item, result_item)
            else:
                result_items.append(result_item)

        self.show_view("results")
        self.enable_compression(False)

        GLib.idle_add(
            self.manager.compress,
            result_items,
            self.update_result_item,
            self.enable_compression,
        )

    def on_lossy_changed(self, toggle, state):
        self.settings.lossy = toggle.get_active_name() == "lossy"

    def banner_change_mode(self, *args):
        self.settings.new_file = True
        self.show_warning_banner()
        self.set_saving_subtitle()

    def on_preferences(self, *args):
        if self.prefs_dialog is not None:
            self.prefs_dialog.force_close()
        self.prefs_dialog = CurtailPrefsDialog(self)
        self.prefs_dialog.present(self)

    def on_about(self, *args):
        about = Adw.AboutDialog(
            application_name="Curtail",
            application_icon="com.github.huluti.Curtail",
            developer_name="Hugo Posnic",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/Huluti/Curtail",
            issue_url="https://github.com/Huluti/Curtail/issues/new",
            version="1.15.1",
            developers=["Hugo Posnic https://github.com/Huluti"],
            designers=[
                "Jakub Steiner https://github.com/jimmac",
                "Tobias Bernard https://github.com/bertob",
            ],
            translator_credits=_("translator-credits"),
            copyright="© Hugo Posnic",
        )
        about.add_credit_section(
            _("Contributors"),
            [
                "Steven Teskey",
                "Andrey Kozlovskiy",
                "Balló György",
                "olokelo",
                "Archisman Panigrahi",
                "Maximiliano",
                "ARAKHNID",
            ],
        )
        about.set_debug_info(debug_infos())
        about.present(self)

    def on_quit(self, *args):
        self.app.quit()
