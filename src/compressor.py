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

import subprocess
from gi.repository import Gtk, Gio, GObject
from shutil import copy2
from pathlib import Path

from .tools import message_dialog, get_file_type


SETTINGS_SCHEMA = 'com.github.huluti.Curtail'


class Compressor():
    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, win, filename, new_filename):
        super().__init__()

        self.win = win

        # Filenames
        self.filename = filename
        self.new_filename = new_filename

        self.file_data = Path(self.filename)
        self.new_file_data = Path(self.new_filename)

        self.full_name = self.file_data.name

        self.size = self.file_data.stat().st_size
        self.new_size = 0
        self.row = None

    def run_command(self, command):
        try:
            subprocess.call(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 shell=True,
                                 timeout=20)
            self.command_finished()

        except Exception as err:
            message_dialog(self.win, _("An error has occured"), str(err))

    def compress_image(self):
        file_type = get_file_type(self.filename)
        if file_type:
            self.row = self.win.create_result_row(self.full_name, self.filename,
                self.new_filename, self.size)
            lossy = self._settings.get_boolean('lossy')
            metadata = self._settings.get_boolean('metadata')
            file_attributes = self._settings.get_boolean('file-attributes')

            if file_type == 'png':
                command = self.build_png_command(lossy, metadata, file_attributes)
            elif file_type == 'jpg':
                command = self.build_jpg_command(lossy, metadata, file_attributes)
            elif file_type == 'webp':
                command = self.build_webp_command(lossy, metadata)
            self.run_command(command)  # compress image

    def command_finished(self):
        # TODO: Check if new size is equal or higher than the old one
        self.new_size = self.new_file_data.stat().st_size

        savings = round(100 - (self.new_size * 100 / self.size), 2)
        self.win.update_result_row(self.row, self.size, self.new_size, savings)

    def build_png_command(self, lossy, metadata, file_attributes):
        pngquant = 'pngquant --quality=0-{} -f "{}" --output "{}"'
        optipng = 'optipng -clobber -o{} "{}" -out "{}"'

        if not metadata:
            pngquant += ' --strip'
            optipng += ' -strip all'

        if file_attributes:
            optipng += ' -preserve'

        png_lossy_level = self._settings.get_int('png-lossy-level')
        png_lossless_level = self._settings.get_int('png-lossless-level')

        if lossy:  # lossy compression
            command = pngquant.format(png_lossy_level, self.filename,
                                      self.new_filename)
            command += ' && '
            command += optipng.format(png_lossless_level, self.new_filename,
                                      self.new_filename)
        else: # lossless compression
            command = optipng.format(png_lossless_level, self.filename,
                                     self.new_filename)
        return command

    def build_jpg_command(self, lossy, metadata, file_attributes):
        do_new_file = self._settings.get_boolean('new-file')
        do_jpg_progressive = self._settings.get_boolean('jpg-progressive')

        if do_new_file:
            jpegoptim = 'jpegoptim --max={} -o -f --stdout "{}" > "{}"'
            jpegoptim2 = 'jpegoptim -o -f --stdout "{}" > "{}"'
        else:
            jpegoptim = 'jpegoptim --max={} -o -f "{}"'
            jpegoptim2 = 'jpegoptim -o -f "{}"'

        if do_jpg_progressive:
            jpegoptim += ' --all-progressive'
            jpegoptim2 += ' --all-progressive'

        if not metadata:
            jpegoptim += ' --strip-all'
            jpegoptim2 += ' --strip-all'

        if file_attributes:
            jpegoptim += ' --preserve --preserve-perms'
            jpegoptim2 += ' --preserve --preserve-perms'

        jpg_lossy_level = self._settings.get_int('jpg-lossy-level')
        if lossy:  # lossy compression
            if do_new_file:
                command = jpegoptim.format(jpg_lossy_level, self.filename,
                                           self.new_filename)
            else:
                command = jpegoptim.format(jpg_lossy_level, self.filename)
        else:  # lossless compression
            if do_new_file:
                command = jpegoptim2.format(self.filename, self.new_filename)
            else:
                command = jpegoptim2.format(self.filename)
        return command

    def build_webp_command(self, lossy, metadata):
        command = "cwebp " + self.filename

        # cwebp doesn't preserve any metadata by default
        if metadata:
            command += " -metadata all"

        if lossy:
            quality = self._settings.get_int('webp-lossy-level')
        else:
            command += " -lossless"
            quality = 100   # maximum cpu power for lossless

        compression_level = self._settings.get_int('webp-lossless-level')

        # multithreaded, (lossless) compression mode, quality, output
        command += " -mt -m {}".format(compression_level)
        command += " -q {}".format(quality)
        command += " -o {}".format(self.new_filename)

        return command

    def feed(self, stdout, condition):
        return True
