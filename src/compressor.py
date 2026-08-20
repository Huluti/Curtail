import os
import logging
import subprocess
import html
from abc import ABC, abstractmethod
from typing import Callable

from gi.repository import Gio, GLib

from .result_item import ResultItem


class Compressor(ABC):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @classmethod
    @abstractmethod
    def get_file_type(cls) -> str:
        return ""

    @abstractmethod
    def build_command(cls, result_item: ResultItem) -> str:
        return ""

    def run(self, result_item: ResultItem, c_update_result_item: Callable) -> None:
        command = self.build_command(result_item)
        try:
            output = subprocess.run(
                command,
                capture_output=True,
                check=True,
                shell=True,
                timeout=self.settings.compression_timeout,
            )
        except subprocess.TimeoutExpired as err:
            logging.error(str(err))
            result_item.error_message = _(
                f"Compression has reached the configured timeout of {self.settings.compression_timeout} seconds."
            )
            result_item.error = True
        except Exception as err:
            result_item.error_message = _("An unknown error has occurred.")
            result_item.error_details_message = html.escape(str(err))
            logging.error(result_item.error_details_message)
            result_item.error = True
            result_item.error_details = True

        if result_item.error:
            GLib.idle_add(c_update_result_item, result_item)
            return

        new_file = Gio.File.new_for_path(result_item.tmp_filename)
        if new_file.query_exists():
            new_file_info = new_file.query_info(
                "standard::size", Gio.FileQueryInfoFlags.NONE
            )
            result_item.new_size = new_file_info.get_size()

            if result_item.new_size >= result_item.size:
                # Output is larger (or equal) than input
                # Don't use compressed temp file
                result_item.skipped = True
            else:
                # Output is smaller than input
                # Copy the compressed temp file
                is_custom_export = self.settings.export_dir_enabled and bool(
                    self.settings.export_dir
                )
                final_path = (
                    result_item.new_filename
                    if (self.settings.new_file or is_custom_export)
                    else result_item.filename
                )
                dest_dir = os.path.dirname(final_path)
                if not os.path.exists(dest_dir):
                    try:
                        os.makedirs(dest_dir, exist_ok=True)
                    except Exception:
                        pass

                source = Gio.File.new_for_path(result_item.tmp_filename)
                dest = Gio.File.new_for_path(final_path)
                source.copy(
                    dest, Gio.FileCopyFlags.OVERWRITE | Gio.FileCopyFlags.ALL_METADATA
                )

            # Remove the temp file
            new_file.delete()
        else:
            logging.error(str(output))
            result_item.error_message = _("Can't find the compressed file")
            result_item.error = True

        GLib.idle_add(c_update_result_item, result_item)
