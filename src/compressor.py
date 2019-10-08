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
from threading import Thread
from os import path

from .tools import sizeof_fmt, message_dialog


class Compressor(Thread):
    def __init__(self, win, data):
        Thread.__init__(self)
        self.win = win
        self.data = data

    def run(self):
        self.compress_image()

    def compress_image(self):
        filename, new_filename, pfilename = self.data

        # Current size
        size = path.getsize(filename)
        size_str = sizeof_fmt(size)

         # Create tree iter
        treeiter = self.win.store.append([pfilename['full_name'],
                                         size_str, '', ''])

        # Compress image
        self.call_compressor(filename, new_filename, pfilename['ext'])

        # Update tree iter
        new_size = path.getsize(new_filename)
        new_size_str = sizeof_fmt(new_size)
        self.win.store.set_value(treeiter, 2, new_size_str)

        savings = round(100 - (new_size * 100 / size), 2)
        savings = '{}%'.format(str(savings))
        self.win.store.set_value(treeiter, 3, savings)

    def call_compressor(self, filename, new_filename, ext):
        if ext == 'png':
            command = ['optipng', '-clobber', '-o2', '-strip', 'all', \
                       filename, '-out', new_filename]
        elif ext == 'jpeg' or ext == 'jpg':
            command = ['jpegtran', '-optimize', '-progressive', \
                       '-outfile', new_filename, filename]
        ret = subprocess.call(command)
        if ret != 0:
            message_dialog(self, 'error', _("An error has occured"),
                           _("\"{}\" has not been minimized.") \
                           .format(pfilename['full_name']))
            return
