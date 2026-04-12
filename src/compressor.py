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
                "Compression has reached the configured timeout of {} seconds."
            ).format(self.settings.compression_timeout)
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
            print(result_item.new_size, result_item.size)

            if result_item.new_size >= result_item.size:
                # Output is larger (or equal) than input
                result_item.skipped = True
            else:
                # Output is smaller than input
                # Copy the compressed temporary file
                final_path = (
                    result_item.new_filename
                    if self.settings.new_file
                    else result_item.filename
                )
                source = Gio.File.new_for_path(result_item.tmp_filename)
                dest = Gio.File.new_for_path(final_path)
                source.copy(
                    dest, Gio.FileCopyFlags.OVERWRITE | Gio.FileCopyFlags.ALL_METADATA
                )

            # Remove the tmp file
            new_file.delete()
        else:
            logging.error(str(output))
            result_item.error_message = _("Can't find the compressed file")
            result_item.error = True

        GLib.idle_add(c_update_result_item, result_item)
