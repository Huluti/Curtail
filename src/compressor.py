import logging
import os
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

    @classmethod
    @abstractmethod
    def has_native_skip_capacity(cls) -> bool:
        return False

    @abstractmethod
    def build_command(cls, result_item: ResultItem) -> str:
        return ""

    def create_tmp_result_item(self, result_item: ResultItem) -> ResultItem:
        """Creates a temporary copy of the file to be compressed rather than the original
        The result_item's information is changed to point to the temporary file
        This is done in case the output is larger than the input in overwrite mode
        """
        base_dir, filename = os.path.split(result_item.filename)
        tmp_filename = os.path.join(base_dir, f".{filename}.tmp")
        result_item.filename = tmp_filename
        result_item.new_filename = tmp_filename

        source = Gio.File.new_for_path(result_item.original_filename)
        dest = Gio.File.new_for_path(result_item.filename)
        source.copy(dest, Gio.FileCopyFlags.COPY_ALL_METADATA)

        return result_item

    def run(self, result_item: ResultItem, c_update_result_item: Callable) -> None:
        if not self.has_native_skip_capacity() and self.settings.new_file:
            result_item = self.create_tmp_result_item(result_item)
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

        new_file = Gio.File.new_for_path(result_item.new_filename)
        if new_file.query_exists():
            new_file_info = new_file.query_info(
                "standard::size", Gio.FileQueryInfoFlags.NONE
            )
            result_item.new_size = new_file_info.get_size()

            # Manually skip files if necessary
            if not self.has_native_skip_capacity():
                # Safe mode
                if self.settings.new_file:
                    if result_item.new_size >= result_item.size:
                        # Output is larger (or equal) than input in safe mode
                        # Remove the new file
                        new_file.delete()
                        result_item.skipped = True
                # Overwrite mode
                else:
                    if result_item.new_size >= result_item.size:
                        # Output is larger (or equal) than input in overwrite mode
                        # Set file as skipped, since the temporary file was compressed
                        # The original file was not changed
                        result_item.skipped = True
                    else:
                        # Output is smaller than input in overwrite mode
                        # Copy the compressed temporary file onto the uncompressed original file
                        source = Gio.File.new_for_path(result_item.filename)
                        dest = Gio.File.new_for_path(result_item.original_filename)
                        source.copy(dest, Gio.FileCopyFlags.COPY_ALL_METADATA)

                    # Remove temporary file that was created for overwrite mode
                    # Also set the result_item's information back to the original file
                    result_item.file.delete()
                    result_item.filename = result_item.original_filename
                    result_item.new_filename = result_item.original_filename

                    new_file = Gio.File.new_for_path(result_item.new_filename)
                    new_file_info = new_file.query_info(
                        "standard::size", Gio.FileQueryInfoFlags.NONE
                    )
                    result_item.new_size = new_file_info.get_size()
            elif result_item.size == result_item.new_size:
                # File was automatically skipped by a compressor
                result_item.skipped = True

                # Remove new file if in safe mode
                if self.settings.new_file:
                    new_file.delete()
        else:
            logging.error(str(output))
            result_item.error_message = _("Can't find the compressed file")
            result_item.error = True

        GLib.idle_add(c_update_result_item, result_item)
