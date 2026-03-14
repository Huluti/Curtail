import subprocess
import logging
from abc import ABC, abstractmethod
from gi.repository import Gio, GLib


class Compressor(ABC):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @classmethod
    @abstractmethod
    def get_file_type(cls) -> str:
        return ""

    @abstractmethod
    def build_command(cls, result_item):
        pass

    def create_tmp_result_item(self, result_item):
        # Creates a temporary copy of the file to be compressed rather than the original
        # The result_item's information is changed to point to the temporary file
        # This is done in case the output is larger than the input in overwrite mode
        index = result_item.filename.find(result_item.name)
        tmp_filename = (
            result_item.filename[:index] + "." + result_item.filename[index:] + ".tmp"
        )
        result_item.filename = tmp_filename
        result_item.new_filename = tmp_filename

        source = Gio.File.new_for_path(result_item.original_filename)
        dest = Gio.File.new_for_path(result_item.filename)
        source.copy(dest, Gio.FileCopyFlags.COPY_ALL_METADATA)

    def run(self, result_item, c_update_result_item):
        error = False
        error_message = ""
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
            error_message = _(
                "Compression has reached the configured timeout of {} seconds."
            ).format(self.settings.compression_timeout)
            error = True
        except Exception as err:
            logging.error(str(err))
            error_message = _("An unknown error has occurred")
            error = True
        finally:
            if not error:
                new_file = Gio.File.new_for_path(result_item.new_filename)
                new_file_info = new_file.query_info(
                    "standard::size", Gio.FileQueryInfoFlags.NONE
                )
                if new_file.query_exists():
                    result_item.new_size = new_file_info.get_size()

                    # Manually skip files if necessary (WebP or SVG)
                    if self.get_file_type() in ["webp", "svg"]:
                        if self.settings.new_file:
                            if result_item.new_size >= result_item.size:
                                # Output is larger (or equal) than input in safe mode
                                # Remove the new file
                                new_file.delete()
                                result_item.skipped = True
                        else:
                            if not result_item.new_size > result_item.size:
                                # Output is smaller than input in overwrite mode
                                # Copy the compressed temporary file onto the uncompressed original file
                                source = Gio.File.new_for_path(result_item.filename)
                                dest = Gio.File.new_for_path(
                                    result_item.original_filename
                                )
                                source.copy(dest, Gio.FileCopyFlags.COPY_ALL_METADATA)
                            else:
                                # Output is smaller than input in overwrite mode
                                # Set file as skipped, since the temporary file was compressed
                                # The original file was not changed
                                result_item.skipped = True

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
                    error_message = _("Can't find the compressed file")
                    error = True

            GLib.idle_add(c_update_result_item, result_item, error, error_message)
