# Change Log
All notable changes to this project will be documented in this file.

## [1.1.0] - 2020-03-12
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
