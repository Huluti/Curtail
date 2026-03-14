from gi.repository import Gio

SETTINGS_SCHEMA = "com.github.huluti.Curtail"


class SettingsManager:
    def __init__(self) -> None:
        self._settings = Gio.Settings.new(SETTINGS_SCHEMA)

    # Genereic setters
    def reset(self, key: str) -> None:
        self._settings.reset(key)

    def set_boolean(self, key: str, value: bool) -> None:
        self._settings.set_boolean(key, value)

    def set_int(self, key: str, value: int) -> None:
        self._settings.set_int(key, value)

    def set_string(self, key: str, value: str) -> None:
        self._settings.set_string(key, value)

    # Options
    @property
    def new_file(self) -> bool:
        return self._settings.get_boolean("new-file")

    @new_file.setter
    def new_file(self, value: bool) -> None:
        self._settings.set_boolean("new-file", value)

    @property
    def naming_mode(self) -> int:
        return self._settings.get_int("naming-mode")

    @naming_mode.setter
    def naming_mode(self, value: int) -> None:
        self._settings.set_int("naming-mode", value)

    @property
    def suffix_prefix(self) -> str:
        return self._settings.get_string("suffix-prefix")

    @suffix_prefix.setter
    def suffix_prefix(self, value: str) -> None:
        self._settings.set_string("suffix-prefix", value)

    @property
    def recursive(self) -> bool:
        return self._settings.get_boolean("recursive")

    @recursive.setter
    def recursive(self, value: bool) -> None:
        self._settings.set_boolean("recursive", value)

    @property
    def compression_timeout(self) -> int:
        return self._settings.get_int("compression-timeout")

    @compression_timeout.setter
    def compression_timeout(self, value: int) -> None:
        self._settings.set_int("compression-timeout", value)

    @property
    def lossy(self) -> bool:
        return self._settings.get_boolean("lossy")

    @lossy.setter
    def lossy(self, value: bool) -> None:
        self._settings.set_boolean("lossy", value)

    @property
    def metadata(self) -> bool:
        return self._settings.get_boolean("metadata")

    @metadata.setter
    def metadata(self, value: bool) -> None:
        self._settings.set_boolean("metadata", value)

    @property
    def file_attributes(self) -> bool:
        return self._settings.get_boolean("file-attributes")

    @file_attributes.setter
    def file_attributes(self, value: bool) -> None:
        self._settings.set_boolean("file-attributes", value)

    # PNG options
    @property
    def png_lossy_level(self) -> int:
        return self._settings.get_int("png-lossy-level")

    @png_lossy_level.setter
    def png_lossy_level(self, value: int) -> None:
        self._settings.set_int("png-lossy-level", value)

    @property
    def png_lossless_level(self) -> int:
        return self._settings.get_int("png-lossless-level")

    @png_lossless_level.setter
    def png_lossless_level(self, value: int) -> None:
        self._settings.set_int("png-lossless-level", value)

    # JPG options
    @property
    def jpg_lossy_level(self) -> int:
        return self._settings.get_int("jpg-lossy-level")

    @jpg_lossy_level.setter
    def jpg_lossy_level(self, value: int) -> None:
        self._settings.set_int("jpg-lossy-level", value)

    @property
    def jpg_progressive(self) -> bool:
        return self._settings.get_boolean("jpg-progressive")

    @jpg_progressive.setter
    def jpg_progressive(self, value: bool) -> None:
        self._settings.set_boolean("jpg-progressive", value)

    # WebP options
    @property
    def webp_lossless_level(self) -> int:
        return self._settings.get_int("webp-lossless-level")

    @webp_lossless_level.setter
    def webp_lossless_level(self, value: int) -> None:
        self._settings.set_int("webp-lossless-level", value)

    @property
    def webp_lossy_level(self) -> int:
        return self._settings.get_int("webp-lossy-level")

    @webp_lossy_level.setter
    def webp_lossy_level(self, value: int) -> None:
        self._settings.set_int("webp-lossy-level", value)

    # SVG options
    @property
    def svg_maximum_level(self) -> bool:
        return self._settings.get_boolean("svg-maximum-level")

    @svg_maximum_level.setter
    def svg_maximum_level(self, value: bool) -> None:
        self._settings.set_boolean("svg-maximum-level", value)
