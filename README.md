# Curtail

<a href="https://circle.gnome.org"><img src="gnome-circle-badge.svg"></a>

## Compress your images

Curtail (previously ImCompressor) is an useful image compressor, supporting PNG, JPEG, WebP and SVG file types.
It support both lossless and lossy compression modes with an option to whether keep or not metadata of images.
It is inspired by [Trimage](https://github.com/Kilian/Trimage) and [Image-Optimizer](https://github.com/GijsGoudzwaard/Image-Optimizer).

### Supported formats

PNG, JPEG, WebP, SVG

## Screenshot

![Curtail](data/screenshots/screen1.png)

## Installation instructions

### Universal package for Linux (recommended)

Curtail is available as a flatpak package.

<a href='https://flathub.org/apps/details/com.github.huluti.Curtail'><img width='240' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

You can also install it by using the following command-line:

    flatpak install flathub com.github.huluti.Curtail
    
### Distro packages

[![Packaging status](https://repology.org/badge/vertical-allrepos/curtail.svg)](https://repology.org/project/curtail/versions)

### Unofficial packages

A [PPA](https://launchpad.net/~apandada1/+archive/ubuntu/curtail) is available for Ubuntu (18.04+) and derivatives:

    sudo add-apt-repository ppa:apandada1/curtail
    sudo apt update
    sudo apt install curtail

A [copr](https://copr.fedorainfracloud.org/coprs/0xmrtt/curtail) package is available for Fedora (36+):

    sudo dnf copr enable 0xmrtt/curtail
    sudo dnf install curtail

### Build from source (nightly)

Build and install by running:

    git clone https://github.com/Huluti/Curtail.git
    cd Curtail
    meson _build
    cd _build
    ninja
    sudo ninja install

The app can then be removed with:

    sudo ninja uninstall

## Tech

Curtail uses a number of open source projects to work properly:

- [GTK 4](https://www.gtk.org)
- [Libadwaita](https://gitlab.gnome.org/GNOME/libadwaita)
- [Python 3](https://www.python.org)
- [Oxipng](https://github.com/shssoichiro/oxipng)
- [pngquant](https://pngquant.org)
- [Jpegoptim](https://github.com/tjko/jpegoptim)
- [libwebp](https://storage.googleapis.com/downloads.webmproject.org/releases/webp/index.html)
- [Scour](https://github.com/scour-project/scour)

## Donations

Do you like the app? Would you like to support its development? Feel free to donate.

[![Liberapay receiving](https://img.shields.io/liberapay/receives/hugoposnic)](https://liberapay.com/hugoposnic)
[![Liberapay patrons](https://img.shields.io/liberapay/patrons/hugoposnic)](https://liberapay.com/hugoposnic)

## License

GNU GENERAL PUBLIC LICENSE (v3)

**Free Software, Yeah!**
