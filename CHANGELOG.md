# Change Log
All notable changes to this project will be documented in this file.

## UNRELEASED

## 1.13.0 - 2025-03-24
### Added
- Add multi-threading.
- Add new preference to select between prefix and suffix for new files. Thank's to @rubenmvc.

### Changed
- Use AdwToggleGroup for lossless/lossy selector. Thank's to @ARAKHN1D.
- Update oxipng.
- Update GNOME Runtime to 48
- Update translations.

## 1.12.0 - 2025-01-05
### Added
- "Open image" and "Show in folder" actions.
- Indicate that file compression was skipped. Thank's to @ARAKHN1D.
- Use file data to guess content type in addition to extension. Thank's to @sheepy0125.

### Changed
- Improve skipping if output is larger than input. Thank's to @ARAKHN1D.
- Update dependencies. Thank's to @PunkPangolin.
- Update translations.

## 1.11.1 - 2024-09-11
### Fixed
- Fix shell injection prevention. Thank's to @ARAKHN1D.

## 1.11.0 - 2024-09-03
### Added
- Always restore original files when compression produces larger files. Thank's to @ARAKHN1D.
- Notify when no files are found in a folder. Thank's to @ARAKHN1D.
- Add Norwegian Bokmaal translations Thank's to @bragefuglseth.

### Changed
- Update translations.
- Use new libadwaita row widgets. Thank's to @bragefuglset and @ARAKHN1D.
- Update Gnome Runtime to 47.

### Fixed
- Fix a shell injection vulnerability. Thank's to @gycsaba96.

## 1.10.0 - 2024-06-07
### Added
- Add a "Recursive Compression" setting.
- Add Bulgarian translation. Thank's to @twlvnn.
- Add Hindi translation. Thank's to @Scrambled777.

### Changed
- Update OxiPNG to v9.1.1
- Update translations.
- Change safe mode directly from warning banner button. Thank's to @ARAKHN1D.

### Fixed
- Fix opening files with "Open With...". Thank's to @ARAKHN1D.
- Fix DnD with nested folders (recursive). Thank's to @ARAKHN1D.
- Fix translations not applied to the help overlay window.

## 1.9.1 - 2024-04-12
### Fixed
- Use default decoration layout for screenshots

## 1.9.0 - 2024-04-12
### Changed
- Correct title case, reword subtitles, remove periods. Thank's to @MonsterObserver.
- Use proper arrow character. Thank's to @kra-mo.
- Update translations.

### Fixed
- Fix drag and drop for folders. Thank's to @ARAKHN1D.
- Appstream data improvements. Thank's to @yakushabb and @bertob.

## 1.8.0 - 2023-11-03
### Added
- Add "Bulk Compress Directory (recursive)" feature. Thank's to @rk234.
- Add simplified Chinese translation. Thank's to @yuhldr.
- Add Ukrainian translation. Thank's to @Vovkiv.
- Add categories and keywords support in appdata. Thank's to @sabriunal.

### Changed
- Improve clarity of preference options.
- Update OxiPNG to v9.
- Update translations.

### Fixed
- Handle cases where previews can't be generated.
- Fix some "Format of this file is not supported".

## [1.7.0] - 2023-04-05

### Added
- SVG support.
- Add a warning banner for overwrite mode.
- New start screen with an AdwStatusPage.
- Add debug information in about window.

### Changed
- Switch from OptiPNG to Oxipng.
- Minor UI improvements.
- Remove some remaining dialogs.
- Bump deps.

### Fixed
- Fix handling of filenames with spaces for WEBP compressor.

## [1.6.0] - 2023-03-31

### Added
- Configurable compression timeout.
- Compress images in an other thread.

### Changed
- Better workflow for headerbar.
- Move saving state in the subtitle.
- Show errors on each line and not in modals anymore.
- Simplify preferences.
- Update translations.

### Fixed
- Fix compression level ranges in UI.

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

