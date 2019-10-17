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
from gi.repository import Gio
from os import path


from .tools import sizeof_fmt, message_dialog, parse_filename


SETTINGS_SCHEMA = 'com.github.huluti.ImCompressor'


class Compressor():
    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, win, filename, new_filename):
        super().__init__()

        self.win = win
        self.filename = filename
        self.new_filename = new_filename

    def compress_image(self):
        # File data
        file_data = parse_filename(self.filename)

        # Current size
        size = path.getsize(self.filename)
        size_str = sizeof_fmt(size)

        # Create tree iter
        if self.filename != self.new_filename:
            file_data2 = parse_filename(self.new_filename)
            full_name = file_data2['full_name']
        else:
            full_name = file_data['full_name']
        treeiter = self.win.store.append([full_name, size_str, '', ''])

        # Compress image
        ret = self.call_compressor(file_data['ext'])
        if ret == 0:
            # Update tree iter
            new_size = path.getsize(self.new_filename)
            new_size_str = sizeof_fmt(new_size)

            savings = round(100 - (new_size * 100 / size), 2)
            savings = '{}%'.format(str(savings))

            self.win.store.set_value(treeiter, 2, new_size_str)
            self.win.store.set_value(treeiter, 3, savings)
        else:
            message_dialog(self.win, 'error', _("An error has occured"),
                           _("\"{}\" has not been minimized.") \
                           .format(full_name))

    def call_compressor(self, ext):
        lossy = self._settings.get_boolean('lossy')

        pngquant = 'pngquant --quality=0-{} -f "{}" --output "{}"'
        optipng = 'optipng -clobber -o{} -strip all "{}" -out "{}"'
        cjpeg = 'cjpeg -quality {} "{}" > "{}"'
        jpegtran = 'jpegtran -optimize -progressive -outfile "{}" "{}"'

        # PNG
        if ext == 'png':
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
        # JPEG
        elif ext in('jpeg', 'jpg'):
            jpg_lossy_level = self._settings.get_int('jpg-lossy-level')
            if lossy:  # lossy compression
                command = cjpeg.format(jpg_lossy_level, self.filename,
                                       self.new_filename,)
            else: # lossless compression
                command = jpegtran.format(self.new_filename, self.filename)
        return self.run_command(command)

    def run_command(self, command):
        try:
            ret = subprocess.call(command, shell=True)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))
            ret = None
        return ret
