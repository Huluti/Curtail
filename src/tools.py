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

from gi.repository import Gtk, GLib, Gio, GdkPixbuf


def sizeof_fmt(num):
    return GLib.format_size(num)


def add_filechooser_filters(dialog):
    all_images = Gtk.FileFilter()
    all_images.set_name(_("All images"))
    all_images.add_mime_type('image/jpeg')
    all_images.add_mime_type('image/png')
    all_images.add_mime_type('image/webp')

    png_images = Gtk.FileFilter()
    png_images.set_name(_("PNG images"))
    png_images.add_mime_type('image/png')

    jpeg_images = Gtk.FileFilter()
    jpeg_images.set_name(_("JPEG images"))
    jpeg_images.add_mime_type('image/jpeg')

    webp_images = Gtk.FileFilter()
    webp_images.set_name(_("WebP images"))
    webp_images.add_mime_type('image/webp')

    file_filters = Gio.ListStore.new(Gtk.FileFilter)
    file_filters.append(all_images)
    file_filters.append(png_images)
    file_filters.append(jpeg_images)
    file_filters.append(webp_images)

    dialog.set_filters(file_filters)


def get_file_type(filename):
    content_type, uncertain = Gio.content_type_guess(filename=str(filename))
    if not uncertain:
        if content_type == 'image/jpeg':
            return 'jpg'
        elif content_type == 'image/png':
            return 'png'
        elif content_type == 'image/webp':
            return 'webp'
        else:
            return None
    else:
        return None


def create_image_from_file(filename, max_width, max_height):
    # Image preview
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)

    # Calculate new dimensions while preserving aspect ratio
    width = pixbuf.get_width()
    height = pixbuf.get_height()

    # If the image is wider than it is tall, scale it to fit the width
    if width > height:
        ratio = max_width / float(width)
        new_width = max_width
        new_height = int(height * ratio)
    # Otherwise, scale it to fit the height
    else:
        ratio = max_height / float(height)
        new_width = int(width * ratio)
        new_height = max_height

    scaled_pixbuf = pixbuf.scale_simple(new_width, new_height,
        GdkPixbuf.InterpType.BILINEAR)

    image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)

    return image
