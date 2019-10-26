# ImCompressor

## Simple & useful image compressor.

[![Maintainability](https://api.codeclimate.com/v1/badges/aae63e7ac1c54526dc9c/maintainability)](https://codeclimate.com/github/Huluti/ImCompressor/maintainability)

ImCompressor is an useful image compressor, supporting PNG and JPEG file types.
It support both lossless and lossy compression modes with an option to whether keep or not metadata of images.
It is inspired by [Trimage](https://github.com/Kilian/Trimage) and [Image-Optimizer](https://github.com/GijsGoudzwaard/Image-Optimizer).

By the same developer as [ImEditor](https://github.com/ImEditor/ImEditor).

### Supported formats

PNG, JPEG

## Screenshot

![ImCompressor](data/screenshots/screen1.png)

## Installation instructions

### Universal package for Linux (recommended)

ImCompressor is available as a flatpak package.

<a href='https://flathub.org/apps/details/com.github.huluti.ImCompressor'><img width='240' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

You can also install it by using the following command-line:

    flatpak install flathub com.github.huluti.ImCompressor
    
### Distro packages

[![Packaging status](https://repology.org/badge/vertical-allrepos/imcompressor.svg)](https://repology.org/project/imcompressor/versions)
    
### Build from source (nightly)

Build and install by running:

    git clone https://github.com/Huluti/ImCompressor.git
    cd ImCompressor
    meson _build
    cd _build
    ninja
    sudo ninja install

The app can then be removed with:

    sudo ninja uninstall

## Tech

ImCompressor uses a number of open source projects to work properly:

- [GTK 3](https://www.gtk.org)
- [Python 3](https://www.python.org)
- [OptiPNG](http://optipng.sourceforge.net)
- [pngquant](https://pngquant.org)
- [Jpegoptim](https://github.com/tjko/jpegoptim)

## Donations

Do you like the app? Would you like to support its development? Feel free to donate.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/hposnic)

## License

GNU GENERAL PUBLIC LICENSE (v3)

**Free Software, Hell Yeah!**
