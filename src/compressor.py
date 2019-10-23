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
from os import path, remove
from shutil import copy2

from .tools import message_dialog, parse_filename


SETTINGS_SCHEMA = 'com.github.huluti.ImCompressor'


class Compressor():
    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    def __init__(self, win, filename, new_filename):
        super().__init__()

        self.win = win

        # Filenames
        self.filename = filename
        self.new_filename = new_filename

        self.file_data = parse_filename(self.filename)
        self.full_name = self.file_data['full_name']

        self.backup_filename  = '{}/.{}.{}'.format(self.file_data['folder'],
            self.file_data['name'], self.file_data['ext'])
        # to fix https://github.com/mozilla/mozjpeg/issues/248
        self.tmp_filename  = '{}/.{}-tmp.{}'.format(self.file_data['folder'],
            self.file_data['name'], self.file_data['ext'])

        # Sizes
        self.size = path.getsize(self.filename)
        self.new_size = 0

    def create_backup_file(self, filename, backup_filename):
        # Do a backup of the original file
        try:
            copy2(filename, backup_filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))
            return False
        return True

    def delete_backup_file(self, backup_filename):
        # Delete backup file
        try:
            remove(backup_filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))
            return False
        return True

    def restore_backup_file(self, filename, new_filename, backup_filename):
        # Restore original backup
        try:
            remove(new_filename)
            copy2(backup_filename, filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))
            return False
        return True

    def compress_image(self):
        keep_going = self.create_backup_file(self.filename, self.backup_filename)
        if not keep_going:
            return

        tree_iter = self.win.create_treeview_row(True, self.full_name, self.size)

        # The operation that blocks the UI
        ret = self.call_compressor(self.file_data['ext'])  # compress image
        # End of the operation that blocks the UI

        self.new_size = path.getsize(self.new_filename)
        is_minus = True
        if self.new_size >= self.size:  # new size is equal or higher than the old one
            is_minus = False
            keep_going = self.restore_backup_file(self.filename,
                                                  self.new_filename,
                                                  self.backup_filename)
            if not keep_going:
                return
        keep_going = self.delete_backup_file(self.backup_filename)
        if not keep_going:
            return

        if ret != 0:
            message_dialog(self.win, 'error', _("An error has occured"),
                           _("\"{}\" has not been minimized.") \
                           .format(self.full_name))
            return
        elif not is_minus:
            message_dialog(self.win, 'info', _("Compression not useful"),
                _("\"{}\": the size of the compressed image is larger than the original size.") \
                .format(self.full_name))
            return

        # Calculate savings in percent
        savings = round(100 - (self.new_size * 100 / self.size), 2)
        self.win.update_treeview_row(tree_iter, self.new_size, savings)

    def call_compressor(self, ext):
        fix_weird_bug = False
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
                if not self._settings.get_boolean('new-file'):  # not using suffix
                    # to fix https://github.com/mozilla/mozjpeg/issues/248
                    keep_going = self.create_backup_file(self.filename,
                                                         self.tmp_filename)
                    if not keep_going:
                        return
                    new_filename = self.tmp_filename
                    fix_weird_bug = True
                else:
                    new_filename = self.new_filename
                command = cjpeg.format(jpg_lossy_level, self.filename,
                                        new_filename)
            else: # lossless compression
                command = jpegtran.format(self.new_filename, self.filename)
        ret = self.run_command(command)

        if fix_weird_bug:
            keep_going = self.restore_backup_file(self.filename, self.filename,
                                                  self.tmp_filename)
            if not keep_going:
                return
            keep_going = self.delete_backup_file(self.tmp_filename)
            if not keep_going:
                return
        return ret

    def run_command(self, command):
        try:
            ret = subprocess.call(command, shell=True)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))
            ret = None
        return ret
