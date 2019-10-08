# ImCompressor

## Simple & lossless image compressor.

[![Maintainability](https://api.codeclimate.com/v1/badges/aae63e7ac1c54526dc9c/maintainability)](https://codeclimate.com/github/Huluti/ImCompressor/maintainability)

ImCompressor is a lossless image compressor.
It is inspired by [Trimage](https://github.com/Kilian/Trimage) and [Image-Optimizer](https://github.com/GijsGoudzwaard/Image-Optimizer).

By the same developer as [ImEditor](paypal.me/hposnic).

### Supported formats

PNG, JPEG

## Screenshot

![ImCompressor](data/screenshots/screen1.png)

## Installation instructions

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
- [MozJPEG](https://github.com/mozilla/mozjpeg)
- [Jpegoptim](https://github.com/tjko/jpegoptim)

## Donations

Do you like the app? Would you like to support its development? Feel free to donate.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/hposnic)

## License

GNU GENERAL PUBLIC LICENSE (v3)

**Free Software, Hell Yeah!**
