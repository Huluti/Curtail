# Change Log
All notable changes to this project will be documented in this file.

## [1.5.0] - 2023-03-25
### Changed
- More modern results page.
- Update translations.

### Fixed
- Reduce images one by one to avoid freezes.

## [1.4.0] - 2023-03-23
### Added
- Port to GTK 4 and Libadwaita.

### Changed
- Update deps.
- Update translations.

### Fixed
- Less annoying 'Apply dialog'.

## [1.3.1] - 2022-07-12
### Added
- Make size columns sortable.
- Add Korean translation. Thank's to @MarongHappy.

### Changed
- Update screenshots.
- Update Turkish translation. Thank's to @libreajans.
- Update French translation. Thank's to @rene-coty.
- Update Dutch translation. Thank's to @Vistaus.

### Fixed
- Fix savings column sorting.

## [1.3.0] - 2022-05-01
### Added
- Add option to preserve file attributes if possible.

### Changed
- Update image libraries.
- Update French translation.
- Update Russian translation. Thank's to @prokoudine.

## [1.2.2] - 2021-11-13
### Added
- Add Turkish translation. Thank's to @05akalan57.
- Add Occitan translation. Thank's to @Mejans.
- Add Galician translation. Thank's to @Fran Dieguez.

### Changed
- Update Dutch translation. Thank's to @Vistaus.
- Update Spanish translation. Thank's to @oscfdezdz.
- Update Dutch translation. Thank's to @Vistaus.
- Update Croatian translation. Thank's to @milotype.
- Update German translation. Thank's to @Etamuk.
- Update Portuguese Brazil translation. Thank's to @fulvio-alves.
- Update Swedish translation. Thank's to @eson57.

## [1.2.1] - 2021-07-04
### Added
- Add 'Apply to all queue' option for existing file dialog.
- Add Polish translation. Thank's to @olokelo.

## [1.2.0] - 2021-06-29
### Added
- Add WebP support. Thank's to @olokelo.
- Add Croatian translation. Thank's to @milotype.

### Changed
- Update Spanish translation. Thank's to oscfdezdz.
- Update Portuguese (Brazil) translation. Thank's to @fulvio-alves.
- Don't accept empty file. Thank's to @akozlovskiy119.
- Better guess of extensions. Thank's to @akozlovskiy119.

### Fixed
- Use correct file listing format for drag-and-drop. Thank's to @akozlovskiy119.
- Fix directory handling. Thank's to @akozlovskiy119.
- Fix missing icon in LXQt, MATE, XFCE (#76). Thank's to @apandada1.

## [1.1.0] - 2021-03-12
### Added
- An option to progressive encode jpegs. Thank's to @trst.
- Add Russian translation.
- Add Slovak translation.
- Add Swedish translation.

### Changed
- Better handling of existing files.
- Better appdata summary.
- Update Spanish translation.

### Fixed
- Compress images with extensions in uppercase.
- Center preferences window header switcher. Thank's to @andrenete.
- Fix columns sorting. Thank's to @andrenete.
- Don't allow empty suffix (incorrect compression for JPEG). Thank's to @andrenete.

## [1.0.0] - 2020-12-19
### Added
- A new name. Thank's to @bertob, @jannuary and @jimmac.
- A new icon designed by @jimmac.
- Support for dragging folders.

## [0.8.4] - 2020-11-15
### Changed
- Just fix a packaging file.

## [0.8.3] - 2020-11-14
### Changed
- Just update GNOME runtime.

## [0.8.2] - 2020-08-11
### Added
- Add Portuguese (Brazil) translation.

### Changed
- Don't use legacy path for metadata.

## [0.8.1] - 2020-04-02
### Fixed
- Fix compression of jpg files that produced 0b files.

## [0.8] - 2019-10-27
### Added
- Add an option to whether keep or not metadata of images.

### Changed
- Replace mozjpeg lib by jpegoptim.
- Update translations.

## [0.7] - 2019-10-25
### Added
- Add a spinner to indicate the progress of the compression.
- Using threads to compress images simultaneously.

### Changed
- Simplification of certain sentences.

### Fixed
- Really don't block the UI anymore when performing compression.

## [0.6] - 2019-10-21
### Added
- Add lossy compression features.
- Add options to change compression levels.
- New layout for the preferences dialog.

### Changed
- Don't permit higher resulting size.
- Better displaying of the drag area.
- Update translations.

### Fixed
- Catch errors in subprocess to avoid crashing the app.

## [0.5.2] - 2019-10-13
### Fixed
- Fix build.

## [0.5.1] - 2019-10-13
### Added
- Add Italian translation.

### Changed
- Update translations.

### Fixed
- Fix opening files from file managers.

## [0.5] - 2019-10-12
### Added
- Toggle the suffix entry according to new file option.
- Scroll automatically to last compressed image in the list.

### Changed
- Add save info label also on homepage and displace it at bottom.

### Fixed
- Improve handling of filenames to avoid some errors (e.g., folders).
- Various fixes.

## [0.4] - 2019-10-11
### Added
- Add a setting to change the '-min' suffix.
- Add some explanations of applied settings.
- Add Ctrl+O shortcut to open files.
- Add Dutch and German translations.
- Display translators' names in about dialog.

### Changed
- Don't block the UI anymore when performing compression.

### Fixed
- Fix size of the preferences window.

## [0.3] - 2019-10-10
### Added
- Add a preferences window with new-file and dark-theme options.

### Changed
- Various UI changes.

## [0.2.2] - 2019-10-10
### Added
- Permit to sort results by name or saving ratio.

### Fixed
- Fix a crash when compressing an image with dots in its name.

## [0.2.1] - 2019-10-09
### Changed
- Stick back and forward buttons.
- Change APP id.

## [0.2] - 2019-10-08
### Changed
- Various optimizations.
- Improve error messages.
- Improve some texts.
- Change description.

## [0.1] - 2019-10-08
### Added
- Initial version.
