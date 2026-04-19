from gi.repository import Gtk, Adw, GObject

from .result_item import ResultItem
from .tools import create_image_from_file

CURTAIL_PATH = "/com/github/huluti/Curtail/"


@Gtk.Template(resource_path=CURTAIL_PATH + "ui/result-item-row.ui")
class CurtailResultItemRow(Adw.ActionRow):
    __gtype_name__ = "CurtailResultItemRow"

    result_item = GObject.Property(type=ResultItem)

    skipped_info_button = Gtk.Template.Child()
    error_info_button = Gtk.Template.Child()
    error_popover_label = Gtk.Template.Child()
    savings_label = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    error_image = Gtk.Template.Child()

    def __init__(self, result_item: ResultItem, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.result_item = result_item

        self.set_title(result_item.name)
        self.set_tooltip_text(result_item.new_filename)
        self.set_subtitle(result_item.subtitle_label)

        if len(result_item.new_filename) > 0:
            image = create_image_from_file(result_item.filename, 48, 48)
            if image:
                self.add_prefix(image)

        result_item.bind_property(
            "savings", self.savings_label, "label", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "subtitle_label", self, "subtitle", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "running", self.spinner, "visible", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "skipped", self.skipped_info_button, "visible", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "error", self.error_image, "visible", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "error_details", self.error_info_button, "visible", GObject.BindingFlags.DEFAULT
        )
        result_item.bind_property(
            "error_details_message",
            self.error_popover_label,
            "label",
            GObject.BindingFlags.DEFAULT
        )
