# Curtail Packaging Troubleshooting

Common issues when building or running Curtail packages.

## AppImage Issues

### AppImage won't run (FUSE missing)
```bash
# Ubuntu/Debian
sudo apt install fuse libfuse2

# Fedora/RHEL
sudo dnf install fuse

# Arch/Manjaro
sudo pacman -S fuse2
```

### Permission denied
```bash
chmod +x curtail-x86_64.AppImage
```

### AppImage runs but Curtail doesn't launch
- Check `~/.local/share/curtail/` for logs
- Ensure required compression tools are installed (see below)
- Run with `--verbose` for debug output

### GLib-GIO-ERROR: Settings schema 'com.github.huluti.Curtail' is not installed
The AppImage must include compiled GSettings schemas. Ensure the build process runs `glib-compile-schemas` on `usr/share/glib-2.0/schemas/`.

## Debian/Ubuntu Package Issues

### dpkg dependency errors
```bash
sudo dpkg -i curtail_*.deb
sudo apt-get install -f  # Fixes missing dependencies
```

### Missing compression tools after install
The `.deb` declares external tools as dependencies. Install manually if needed:
```bash
sudo apt install oxipng pngquant jpegoptim webp scour
```

### Python module not found (gi, adw, etc)
Ensure system packages are installed:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

## Common Runtime Issues

### "Compression tool not found" warnings
Curtail will show in-app warnings if external tools are missing. Install the required tool for the format you're compressing.

### PNG compression fails
```bash
# Verify tools work
oxipng --version
pngquant --version
```

### JPEG compression fails
```bash
jpegoptim --version
```

### WebP compression fails
```bash
cwebp -version
```

### SVG compression fails
```bash
scour --version
```

### App doesn't appear in application menu
```bash
# Update desktop database
sudo update-desktop-database

# Update icon cache
gtk-update-icon-cache -f -t /usr/share/icons/hicolor
```

### Flatpak vs system package conflicts
If both Flatpak and .deb/AppImage are installed, they share `~/.local/share/curtail/` config. This is fine but may cause version confusion.

## Build Issues (CI/CD)

### appimagetool: "AppStream metadata missing"
Warning only, not an error. Add `usr/share/metainfo/com.github.huluti.Curtail.appdata.xml` to silence.

### debuild: "Source format '3.0 (quilt)' not supported"
Ensure `debian/source/format` contains `3.0 (quilt)`.

### Python bytecode compilation errors
The package uses `dh_python3` which handles bytecode. If it fails:
```bash
# In debian/rules, override:
override_dh_python3:
	dh_python3 --no-compile
```

## Distribution-Specific Notes

### Ubuntu 22.04
- `libadwaita-1` available in universe
- `oxipng` in universe (install: `sudo apt install oxipng`)

### Ubuntu 24.04+
- All dependencies in main/universe
- `python3.12` default

### Debian 12 (Bookworm)
- `libadwaita-1` in backports
- `oxipng` may need backports or manual install

### Fedora 39/40
- Works with `dnf install ./curtail.rpm`
- Uses libssl3

### Arch Linux (for manual .deb conversion)
```bash
pacman -S oxipng pngquant jpegoptim libwebp scour
```

### openSUSE Tumbleweed/Leap
- Use `alien --to-rpm` then `zypper in ./curtail.rpm`

## Reporting Issues

If you encounter a packaging issue:
1. Check this file first
2. Run with verbose output: `./curtail-x86_64.AppImage --verbose`
3. Check `~/.local/share/curtail/logs/`
4. Open issue on [GitHub](https://github.com/Huluti/Curtail/issues)

Include:
- Distro & version
- Package format (AppImage/.deb)
- Error message
- `ldd usr/bin/curtail` output (for missing libs)