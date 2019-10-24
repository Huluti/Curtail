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
import shlex
from gi.repository import Gio, GObject
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
        self.fix_jpg_weird_bug = False
        self.tmp_filename  = '{}/.{}-tmp.{}'.format(self.file_data['folder'],
            self.file_data['name'], self.file_data['ext'])

        self.size = path.getsize(self.filename)
        self.new_size = 0
        self.tree_iter = None

    def create_backup_file(self, filename, backup_filename):
        # Do a backup of the original file
        try:
            copy2(filename, backup_filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))

    def delete_backup_file(self, backup_filename):
        # Delete backup file
        try:
            remove(backup_filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))

    def restore_backup_file(self, filename, new_filename, backup_filename):
        # Restore original backup
        try:
            remove(new_filename)
            copy2(backup_filename, filename)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))

    def run_command(self, command):
        try:
            p = subprocess.Popen(shlex.split(command),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
            self.io_id = GObject.io_add_watch(p.stdout, GObject.IO_IN, self.feed)
            GObject.io_add_watch(p.stdout, GObject.IO_HUP, self.command_finished)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))

    def compress_image(self):
        self.create_backup_file(self.filename, self.backup_filename)

        self.tree_iter = self.win.create_treeview_row(self.full_name, self.size)

        lossy = self._settings.get_boolean('lossy')
        if self.file_data['ext'] == 'png':
            command = self.build_png_command(lossy)
        elif self.file_data['ext'] in('jpeg', 'jpg'):
            command = self.build_jpg_command(lossy)
        self.run_command(command)  # compress image

    def command_finished(self, stdout, condition):
        GObject.source_remove(self.io_id)
        stdout.close()

        self.new_size = path.getsize(self.new_filename)
        savings = round(100 - (self.new_size * 100 / self.size), 2)

        self.win.update_treeview_row(self.tree_iter, self.new_size, savings)

        # Check if new size is equal or higher than the old one
        if self.new_size >= self.size:
            self.restore_backup_file(self.filename, self.new_filename,
                                     self.backup_filename)
            message_dialog(self.win, 'info', _("Compression not useful"),
                _("\"{}\": the image is already compressed.") \
                .format(self.full_name))
        self.delete_backup_file(self.backup_filename)

        # Handle cjpeg weird bug
        if self.fix_jpg_weird_bug:
            self.restore_backup_file(filename, self.filename,
                                     self.tmp_filename)
            self.delete_backup_file(self.tmp_filename)

    def build_png_command(self, lossy):
        pngquant = 'pngquant --quality=0-{} -f "{}" --output "{}"'
        optipng = 'optipng -clobber -o{} -strip all "{}" -out "{}"'

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

    def build_jpg_command(self, lossy):
        cjpeg = 'cjpeg -quality {} "{}" > "{}"'
        jpegtran = 'jpegtran -optimize -progressive -outfile "{}" "{}"'

        jpg_lossy_level = self._settings.get_int('jpg-lossy-level')
        if lossy:  # lossy compression
            if not self._settings.get_boolean('new-file'):  # not using suffix
                # to fix https://github.com/mozilla/mozjpeg/issues/248
                self.create_backup_file(self.filename, self.tmp_filename)
                new_filename = self.tmp_filename
                self.fix_jpg_weird_bug = True
            else:
                new_filename = self.new_filename
            command = cjpeg.format(jpg_lossy_level, self.filename,
                                    new_filename)
        else:  # lossless compression
            command = jpegtran.format(self.new_filename, self.filename)
        return command

    def feed(self, stdout, condition):
        return True
