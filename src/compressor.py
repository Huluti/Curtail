# compressor.py
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

import threading
import subprocess
import logging
import shutil
import os
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib, Gio
from pathlib import Path
from shlex import quote

from .tools import get_file_type


SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


class Compressor():
    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, result_items, c_update_result_item, c_enable_compression):
        super().__init__()

        self.result_items = result_items
        self.c_update_result_item = c_update_result_item
        self.c_enable_compression = c_enable_compression

        # Options
        self.do_new_file = self._settings.get_boolean('new-file')
        self.compression_timeout = self._settings.get_int('compression-timeout')
        self.lossy = self._settings.get_boolean('lossy')
        self.metadata = self._settings.get_boolean('metadata')
        self.file_attributes = self._settings.get_boolean('file-attributes')

        # Format options
        self.png_lossy_level = self._settings.get_int('png-lossy-level')
        self.png_lossless_level = self._settings.get_int('png-lossless-level')

        self.jpg_lossy_level = self._settings.get_int('jpg-lossy-level')
        self.jpg_progressive = self._settings.get_boolean('jpg-progressive')

        self.webp_lossless_level = self._settings.get_int('webp-lossless-level')
        self.webp_lossy_level = self._settings.get_int('webp-lossy-level')

        self.svg_maximum_level = self._settings.get_boolean('svg-maximum-level')

    def create_tmp_result_item(self, result_item):
        # Creates a temporary copy of the file to be compressed rather than the original
        # The result_item's information is changed to point to the temporary file
        # This is done in case the output is larger than the input in overwrite mode
        index = result_item.filename.find(result_item.name)
        tmp_filename = result_item.filename[:index] + "." + result_item.filename[index:] + ".tmp"
        result_item.filename = tmp_filename
        result_item.new_filename = tmp_filename
        shutil.copy2(result_item.original_filename, result_item.filename)

    def compress_images(self):
        thread = threading.Thread(target=self._compress_images)
        thread.start()

    def _compress_images(self):
        cpu_count = os.cpu_count()
        executor = ThreadPoolExecutor(max_workers=cpu_count)
        futures = []
        for result_item in self.result_items:
            file_type = get_file_type(result_item.filename)
            if file_type:
                if file_type == 'png':
                    command = self.build_png_command(result_item)
                elif file_type == 'jpg':
                    command = self.build_jpg_command(result_item)
                elif file_type == 'webp': # Must be manually skipped
                    if not self.do_new_file:
                        self.create_tmp_result_item(result_item)
                    command = self.build_webp_command(result_item)
                elif file_type == 'svg': # Must be manually skipped
                    if not self.do_new_file:
                        self.create_tmp_result_item(result_item)
                    command = self.build_svg_command(result_item)
                future = executor.submit(self.run_command, command, result_item)
                futures.append(future)

        for future in futures:
            future.result()
        GLib.idle_add(self.c_enable_compression, True)

    def run_command(self, command, result_item):
        error = False
        error_message = ''
        try:
            output = subprocess.run(command,
                             capture_output=True,
                             check=True,
                             shell=True,
                             timeout=self.compression_timeout)
        except subprocess.TimeoutExpired as err:
            logging.error(str(err))
            error_message = _('Compression has reached the configured timeout of {} seconds.').format(self.compression_timeout)
            error = True
        except Exception as err:
            logging.error(str(err))
            error_message = _('An unknown error has occurred')
            error = True
        finally:
            if not error:
                new_file_data = Path(result_item.new_filename)
                if new_file_data.is_file():
                    result_item.new_size = new_file_data.stat().st_size

                    # Manually skip files if necessary (WebP or SVG)
                    if get_file_type(result_item.original_filename) in ["webp", "svg"]:
                        if self.do_new_file:
                            if result_item.new_size >= result_item.size:
                                # Output is larger (or equal) than input in safe mode
                                # Remove the new file
                                Path(result_item.new_filename).unlink(True)
                                result_item.skipped = True
                        else:
                            if not result_item.new_size > result_item.size:
                                # Output is smaller than input in overwrite mode
                                # Copy the compressed temporary file onto the uncompressed original file
                                shutil.copy2(result_item.filename, result_item.original_filename)
                            else:
                                # Output is smaller than input in overwrite mode
                                # Set file as skipped, since the temporary file was compressed
                                # The original file was not changed
                                result_item.skipped = True

                            # Remove temporary file that was created for overwrite mode
                            # Also set the result_item's information back to the original file
                            Path(result_item.filename).unlink(True)
                            result_item.filename = result_item.original_filename
                            result_item.new_filename = result_item.original_filename
                            new_file_data = Path(result_item.new_filename)
                            result_item.new_size = new_file_data.stat().st_size
                    elif result_item.size == result_item.new_size:
                        # File was automatically skipped by a compressor
                        result_item.skipped = True

                        # Remove new file if in safe mode
                        if self.do_new_file:
                            Path(result_item.new_filename).unlink(True)
                else:
                    logging.error(str(output))
                    error_message = _("Can't find the compressed file")
                    error = True

            GLib.idle_add(self.c_update_result_item, result_item, error, error_message)

    def build_png_command(self, result_item):
        pngquant = 'pngquant --quality=0-{} -f {} --output {} --skip-if-larger'
        oxipng = 'oxipng -o {} -i 1 {} --out {}'

        if not self.metadata:
            pngquant += ' --strip'
            oxipng += ' --strip safe'

        if self.file_attributes:
            oxipng += ' --preserve'

        if self.lossy:  # lossy compression
            command = pngquant.format(self.png_lossy_level, quote(result_item.filename),
                                      quote(result_item.new_filename))
            command += ' && '
            command += oxipng.format(self.png_lossless_level, quote(result_item.new_filename),
                                      quote(result_item.new_filename))
        else: # lossless compression
            command = oxipng.format(self.png_lossless_level, quote(result_item.filename),
                                     quote(result_item.new_filename))
        return command

    def build_jpg_command(self, result_item):
        if self.do_new_file:
            jpegoptim = 'jpegoptim --max={} -o --stdout {} > {}'
            jpegoptim2 = 'jpegoptim -o --stdout {} > {}'
        else:
            jpegoptim = 'jpegoptim --max={} -o {}'
            jpegoptim2 = 'jpegoptim -o {}'

        if self.jpg_progressive:
            jpegoptim += ' --all-progressive'
            jpegoptim2 += ' --all-progressive'

        if not self.metadata:
            jpegoptim += ' --strip-all'
            jpegoptim2 += ' --strip-all'

        if self.file_attributes:
            jpegoptim += ' --preserve --preserve-perms'
            jpegoptim2 += ' --preserve --preserve-perms'

        if self.lossy:  # lossy compression
            if self.do_new_file:
                command = jpegoptim.format(self.jpg_lossy_level, quote(result_item.filename),
                                           quote(result_item.new_filename))
            else:
                command = jpegoptim.format(self.jpg_lossy_level, quote(result_item.filename))
        else:  # lossless compression
            if self.do_new_file:
                command = jpegoptim2.format(quote(result_item.filename), quote(result_item.new_filename))
            else:
                command = jpegoptim2.format(quote(result_item.filename))
        return command

    def build_webp_command(self, result_item):
        command = 'cwebp {}'.format(quote(result_item.filename))

        # cwebp doesn't preserve any metadata by default
        if self.metadata:
            command += ' -metadata all'

        if self.lossy:
            quality = self.webp_lossy_level
        else:
            command += ' -lossless'
            quality = 100   # maximum cpu power for lossless

        # multithreaded, (lossless) compression mode, quality, output
        command += ' -mt -m {}'.format(self.webp_lossless_level)
        command += ' -q {}'.format(quality)
        command += ' -o {}'.format(quote(result_item.new_filename))

        return command

    def build_svg_command(self, result_item):
        # workaround for https://github.com/scour-project/scour/issues/129
        temp_new_filename = result_item.new_filename
        if not self.do_new_file:
            temp_new_filename = '{}.temp'.format(result_item.new_filename)

        command = 'scour -i {} -o {}'.format(quote(result_item.filename), quote(temp_new_filename))

        if self.svg_maximum_level:
            command += ' --enable-viewboxing --enable-id-stripping'
            command += ' --enable-comment-stripping --shorten-ids --indent=none'

        if not self.do_new_file:
            command += ' && mv {} {}'.format(quote(temp_new_filename), quote(result_item.new_filename))

        return command

