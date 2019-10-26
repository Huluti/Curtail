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

        self.backup_filename  = '{}/.{}-backup.{}'.format(self.file_data['folder'],
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
            p = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 shell=True)
            self.io_id = GObject.io_add_watch(p.stdout, GObject.IO_IN, self.feed)
            GObject.io_add_watch(p.stdout, GObject.IO_HUP, self.command_finished)
        except Exception as err:
            message_dialog(self.win, 'error', _("An error has occured"),
                           str(err))

    def compress_image(self):
        self.create_backup_file(self.filename, self.backup_filename)

        self.tree_iter = self.win.create_treeview_row(self.full_name, self.size)

        lossy = self._settings.get_boolean('lossy')
        metadata = self._settings.get_boolean('metadata')
        if self.file_data['ext'] == 'png':
            command = self.build_png_command(lossy, metadata)
        elif self.file_data['ext'] in('jpeg', 'jpg'):
            command = self.build_jpg_command(lossy, metadata)
        self.run_command(command)  # compress image

    def command_finished(self, stdout, condition):
        GObject.source_remove(self.io_id)
        stdout.close()

        self.new_size = path.getsize(self.new_filename)

        # Check if new size is equal or higher than the old one
        if self.new_size >= self.size:
            self.restore_backup_file(self.filename, self.new_filename,
                                     self.backup_filename)
            self.win.update_treeview_row(self.tree_iter, '/', _("Nothing"))
            message_dialog(self.win, 'info', _("Compression not useful"),
                _("{} is already compressed at max with current options.") \
                           .format(self.full_name))
        else:
            savings = round(100 - (self.new_size * 100 / self.size), 2)
            self.win.update_treeview_row(self.tree_iter, self.new_size,
                                         '{}%'.format(str(savings)))
        self.delete_backup_file(self.backup_filename)

    def build_png_command(self, lossy, metadata):
        pngquant = 'pngquant --quality=0-{} -f "{}" --output "{}"'
        optipng = 'optipng -clobber -o{} "{}" -out "{}"'

        if not metadata:
            pngquant += ' --strip'
            optipng += ' -strip all'

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

    def build_jpg_command(self, lossy, metadata):
        jpegoptim = 'jpegoptim --max={} -o -f --stdout "{}" > "{}"'
        jpegoptim2 = 'jpegoptim -o -f --stdout "{}" > "{}"'

        if not metadata:
            jpgoptim += ' --strip-all'
            jpegoptim2 += ' --strip-all'

        jpg_lossy_level = self._settings.get_int('jpg-lossy-level')
        if lossy:  # lossy compression
            command = jpegoptim.format(jpg_lossy_level, self.filename,
                                    self.new_filename)
        else:  # lossless compression
            command = jpegoptim2.format(self.filename, self.new_filename)
        return command

    def feed(self, stdout, condition):
        return True
