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
from gi.repository import Gtk, GLib, Gio, GObject
from shutil import copy2
from pathlib import Path

from .tools import message_dialog, get_file_type


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
        self.do_jpg_progressive = self._settings.get_boolean('jpg-progressive')

        self.webp_lossless_level = self._settings.get_int('webp-lossless-level')
        self.webp_lossy_level = self._settings.get_int('webp-lossy-level')

    def compress_images(self):
        self.thread = threading.Thread(target=self._compress_images)
        self.thread.start()

    def _compress_images(self):
        for result_item in self.result_items:
            file_type = get_file_type(result_item.filename)
            if file_type:
                if file_type == 'png':
                    command = self.build_png_command(result_item)
                elif file_type == 'jpg':
                    command = self.build_jpg_command(result_item)
                elif file_type == 'webp':
                    command = self.build_webp_command(result_item)
                self.run_command(command, result_item)  # compress image
        GLib.idle_add(self.c_enable_compression, True)

    def run_command(self, command, result_item):
        error = False
        error_message = ''
        try:
            subprocess.call(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 shell=True,
                                 timeout=self.compression_timeout)
        except subprocess.TimeoutExpired:
            error_message = _("Compression has reached the configured timeout of {} seconds.").format(self.compression_timeout)
            error = True
        except Exception as err:
            error_message = _("An unknown error has occured.")
            error = True
        finally:
            self.command_finished(result_item, error, error_message)

    def command_finished(self, result_item, error, error_message):
        if not error:
            new_file_data = Path(result_item.new_filename)
            result_item.new_size = new_file_data.stat().st_size

        GLib.idle_add(self.c_update_result_item, result_item, error, error_message)

    def build_png_command(self, result_item):
        pngquant = 'pngquant --quality=0-{} -f "{}" --output "{}"'
        optipng = 'optipng -clobber -o{} "{}" -out "{}"'

        if not self.metadata:
            pngquant += ' --strip'
            optipng += ' -strip all'

        if self.file_attributes:
            optipng += ' -preserve'

        if self.lossy:  # lossy compression
            command = pngquant.format(self.png_lossy_level, result_item.filename,
                                      result_item.new_filename)
            command += ' && '
            command += optipng.format(self.png_lossless_level, result_item.new_filename,
                                      result_item.new_filename)
        else: # lossless compression
            command = optipng.format(self.png_lossless_level, result_item.filename,
                                     result_item.new_filename)
        return command

    def build_jpg_command(self, result_item):
        if self.do_new_file:
            jpegoptim = 'jpegoptim --max={} -o -f --stdout "{}" > "{}"'
            jpegoptim2 = 'jpegoptim -o -f --stdout "{}" > "{}"'
        else:
            jpegoptim = 'jpegoptim --max={} -o -f "{}"'
            jpegoptim2 = 'jpegoptim -o -f "{}"'

        if self.do_jpg_progressive:
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
                command = jpegoptim.format(self.jpg_lossy_level, result_item.filename,
                                           result_item.new_filename)
            else:
                command = jpegoptim.format(self.jpg_lossy_level, result_item.filename)
        else:  # lossless compression
            if self.do_new_file:
                command = jpegoptim2.format(result_item.filename, result_item.new_filename)
            else:
                command = jpegoptim2.format(result_item.filename)
        return command

    def build_webp_command(self, result_item):
        command = 'cwebp ' + result_item.filename

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
        command += ' -o {}'.format(result_item.new_filename)

        return command

