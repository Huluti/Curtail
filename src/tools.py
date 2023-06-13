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

import re
import platform
import subprocess
from gi.repository import Gtk, GLib, Gio, GdkPixbuf


def sizeof_fmt(num):
    return GLib.format_size(num)


def add_filechooser_filters(dialog):
    all_images = Gtk.FileFilter()
    all_images.set_name(_("All images"))
    all_images.add_mime_type('image/jpeg')
    all_images.add_mime_type('image/png')
    all_images.add_mime_type('image/webp')
    all_images.add_mime_type('image/svg+xml')

    png_images = Gtk.FileFilter()
    png_images.set_name(_("PNG images"))
    png_images.add_mime_type('image/png')

    jpeg_images = Gtk.FileFilter()
    jpeg_images.set_name(_("JPEG images"))
    jpeg_images.add_mime_type('image/jpeg')

    webp_images = Gtk.FileFilter()
    webp_images.set_name(_("WebP images"))
    webp_images.add_mime_type('image/webp')

    svg_images = Gtk.FileFilter()
    svg_images.set_name(_("SVG images"))
    svg_images.add_mime_type('image/svg+xml')

    file_filters = Gio.ListStore.new(Gtk.FileFilter)
    file_filters.append(all_images)
    file_filters.append(png_images)
    file_filters.append(jpeg_images)
    file_filters.append(webp_images)
    file_filters.append(svg_images)

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
        elif content_type == 'image/svg+xml':
            return 'svg'
        else:
            return None
    else:
        return None


def create_image_from_file(filename, max_width, max_height):
    # Image preview
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    except:
        return None

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
    if new_width > new_height:
        image.set_pixel_size(new_width)
    else:
        image.set_pixel_size(new_height)

    return image


def debug_infos():
    python_version = platform.python_version()

    gtk_version = '{}.{}.{}'.format(Gtk.get_major_version(),
        Gtk.get_minor_version(), Gtk.get_micro_version())

     # Jpegoptim
    try:
        jpegoptim = subprocess.check_output(['jpegoptim', '--version'])
        jpegoptim = extract_version(jpegoptim.decode('utf-8'))
    except Exception:
        jpegoptim = _('Version not found')

    # Oxipng
    try:
        oxipng = subprocess.check_output(['oxipng', '--version'])
        oxipng = extract_version(oxipng.decode('utf-8'))
    except Exception:
        oxipng = _('Version not found')

    # pngquant
    try:
        pngquant = subprocess.check_output(['pngquant', '--version'])
        pngquant = extract_version(pngquant.decode('utf-8'))
    except Exception:
        pngquant = _('Version not found')

    # Libwebp
    try:
        libwebp = subprocess.check_output(['cwebp', '-version'])
        libwebp = extract_version(libwebp.decode('utf-8'))
    except Exception:
        libwebp = _('Version not found')

    # Scour
    try:
        scour = subprocess.check_output(['scour', '--version'])
        scour = extract_version(scour.decode('utf-8'))
    except Exception:
        scour = _('Version not found')

    debug = '''Python: {}\n
Gtk: {}\n
Jpegoptim: {}\n
Oxipng: {}\n
pngquant: {}\n
Libwebp: {}\n
Scour: {}\n'''.format(
    python_version,
    gtk_version,
    jpegoptim,
    oxipng,
    pngquant,
    libwebp,
    scour
)

    return debug

def extract_version(text):
    # regular expression to match the version string,
    # consists of three groups of one or more digits separated by dots
    version_regex = r"(\d+\.\d+\.\d+)"

    match = re.search(version_regex, text)
    if match:
        version_string = match.group(1) # extract the version string from the match object
        return version_string
    else:
        return _('Version not found')
