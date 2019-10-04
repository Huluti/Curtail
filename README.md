# ImCompressor

## Simple & useful image compressor.

ImCompressor is a lossless image compressor.

### Supported formats

PNG, JPEG

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

ImEditor uses a number of open source projects to work properly:

- [GTK 3](https://www.gtk.org)
- [Python 3](https://www.python.org)
- [MozJPEG](https://github.com/mozilla/mozjpeg)
- [Jpegoptim](https://github.com/tjko/jpegoptim)

## License

GNU GENERAL PUBLIC LICENSE (v3)

**Free Software, Hell Yeah!**
