import os
from gi.repository import Gio

from .result_item import ResultItem
from .tools import sizeof_fmt


ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/svg+xml"}


class ResultItemManager:
    def __init__(self, settings_manager):
        self.settings = settings_manager

    def build(self, file) -> ResultItem:
        result_item = ResultItem()

        if not file.query_exists():
            result_item.set_error(_("This file doesn't exist."))
            return result_item

        # Get file info
        file_info = file.query_info(
            "standard::display-name,standard::size,standard::content-type,xattr::document-portal.host-path",
            Gio.FileQueryInfoFlags.NONE,
        )

        # Get path by checking host path
        host_path = file_info.get_attribute_string("xattr::document-portal.host-path")
        result_item.filename = host_path if host_path else file.get_path()

        # Display name
        display_name = file_info.get_display_name()
        result_item.name = display_name if display_name else file.get_basename()

        # Check format
        result_item.size = file_info.get_size()
        result_item.mime_type = file_info.get_content_type()
        if result_item.mime_type not in ALLOWED_MIME_TYPES or result_item.size <= 0:
            result_item.set_error(_("Format of this file is not supported."))
            return result_item

        result_item.subtitle_label = sizeof_fmt(result_item.size)

        # New path
        result_item.new_filename = self.create_new_filename(result_item.filename)

        # Tmp path
        base_dir, fname = os.path.split(result_item.new_filename)
        result_item.tmp_filename = os.path.join(base_dir, f".{fname}.tmp")

        return result_item

    def create_new_filename(self, path):
        new_filename = path
        basename = os.path.basename(path)
        splitext = os.path.splitext(basename)
        parent = path.replace(basename, "")
        stem = splitext[0]
        extension = splitext[1]
        suffix_prefix = self.settings.suffix_prefix

        # Use new file or not
        if self.settings.new_file:
            if self.settings.naming_mode == 0:  # Suffix selected
                new_filename = f"{parent}/{stem}{suffix_prefix}{extension}"
            else:  # Prefix selected
                new_filename = f"{parent}/{suffix_prefix}{stem}{extension}"

        return new_filename
