# tools.py
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

from gi.repository import Gtk
from os import path


def sizeof_fmt(num):
    for unit in ['','Kb','Mb']:
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f %s" % (num, 'Yb')


def message_dialog(parent, dialog_type, title, text):
    """Simplify way to show a message in a dialog"""
    button_type = Gtk.ButtonsType.OK
    if dialog_type == 'info':
        dialog_type = Gtk.MessageType.INFO
    elif dialog_type == 'warning':
        dialog_type = Gtk.MessageType.WARNING
    elif dialog_type == 'error':
        dialog_type = Gtk.MessageType.ERROR
    elif dialog_type == 'question':
        dialog_type = Gtk.MessageType.QUESTION
        button_type = Gtk.ButtonsType.YES_NO
    dialog = Gtk.MessageDialog(parent, 0, dialog_type, button_type, title)
    dialog.format_secondary_text(text)
    response = dialog.run()
    dialog.destroy()
    return response


def parse_filename(filename):
    parse_filename = path.split(filename)
    parse_name = parse_filename[1].rsplit('.', 1)
    file_data = {
        'folder': parse_filename[0],
        'full_name': parse_filename[1],
        'name': parse_name[0],
        'ext': parse_name[1].lower()
    }
    return file_data


def add_filechooser_filters(dialog):
    all_images = Gtk.FileFilter()
    all_images.set_name(_("All images"))
    all_images.add_mime_type('image/jpeg')
    all_images.add_mime_type('image/png')

    png_images = Gtk.FileFilter()
    png_images.set_name(_("PNG images"))
    png_images.add_mime_type('image/png')

    jpeg_images = Gtk.FileFilter()
    jpeg_images.set_name(_("JPEG images"))
    jpeg_images.add_mime_type('image/jpeg')

    dialog.add_filter(all_images)
    dialog.add_filter(png_images)
    dialog.add_filter(jpeg_images)
