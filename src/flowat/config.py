from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
    DuplicateSectionError
)
from typing import Any
from pathlib import Path
from sys import platform


if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Flowat")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "config")
    LOG_PATH = Path(FLOWAT_FILES_PATH, "log")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Flowat")
    CONFIG_PATH = Path.home().joinpath(".config", "Flowat")
    LOG_PATH = Path.home().joinpath(".local", "state", "Flowat", "log")

for dir in [FLOWAT_FILES_PATH, CONFIG_PATH, LOG_PATH]:
    dir.mkdir(parents=True, exist_ok=True)


# https://stackoverflow.com/a/31909086
def get_parser(filename: str) -> ConfigParser:
    parser = ConfigParser()
    config_file = Path(CONFIG_PATH, f"{filename}.ini")
    config_file.touch(exist_ok=True)
    parser.read(config_file)
    parser._config_file = config_file
    return parser


def get_default_parser() -> ConfigParser:
    return get_parser(filename="prefs")


class _Config:
    def __init__(self, parser_factory, section: str, key: str, default: Any | None):
        """Parent that sets logic for interacting with a key that returns a
        single value on a specific configuration file.
        """
        self._parser, self._section, self._key, self._default = (
            parser_factory(), section, key, default
        )
        if not parser.has_section(section):
            parser.add_section(section=section)

    def _refresh(self):
        self._parser.read(self._parser._config_file)

    @classmethod
    def get(cls):
        """Refresh the parser with the current data and return the expected value."""
        config_obj = cls()
        return cls.__get()

    @classmethod
    def set(cls):
        """Write `value` to the configuration file."""
        config_obj = cls()
        config_obj.__set(value)

    def __set(self, value: Any):
        self._parser.set(self._section, self._key, str(value))

    def __get() -> Any:
        self._refresh()
        return self._parser.get(self._section, self._key, fallback=self._default)


class _ConfigList:
    def __init__(self, parser_factory, section: str, key: str, default: Any | None):
        """Parent that sets logic for interacting with a key that returns a
        list of values on a specific configuration file.
        """
        self._parser, self._section, self._key, self._default = (
            parser_factory(), section, key, default
        )
        if not parser.has_section(section):
            parser.add_section(section=section)

    def _refresh(self):
        self._parser.read(self._parser._config_file)

    def __get(self) -> list[str]:
        """Get list from config file as a python list of strings."""
        string = string.replace("[", "").replace("]", "")
        list_of_items = string.split(",")
        return [i.strip() for i in list_of_items if i.strip() != ""]

    def __set(self, value: list[str]) -> str:
        """Writes a a python list to the config file, replacing the existing one."""
        string_list = (
            str(list_).replace("[", "[\n\t").replace(
                ", ", ",\n\t").replace("'", "")
        )
        return string_list.replace("\\\\", "\\")

    def __add(self, value: Any):
        """Adds a `value` to the config list."""

    def __rm(self, value: Any):
        """Removes `value` from config list if it is present."""



class BackupPlaces(_ConfigList):
    def __init__(self):
        super().__init__(
            parser_factory=get_default_parser,
            section="backup",
            key="backup_places",
            default=None,
        )
