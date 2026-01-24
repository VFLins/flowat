from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
    DuplicateSectionError,
)
from typing import Any, Callable, Iterator
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


def get_parser(filename: str) -> ConfigParser:
    """Base function for parser factories to be used internally by config classes.
    The parser factories should not take any input value, and return this function's
    return value with the same inputs.

    :filename: Name of the config file without extension.
    """
    parser = ConfigParser()
    config_file = Path(CONFIG_PATH, f"{filename}.ini")
    config_file.touch(exist_ok=True)
    parser.read(config_file)
    parser._config_file = config_file
    return parser


def get_default_parser() -> ConfigParser:
    """Factory of parsers for the 'prefs.ini' config file."""
    return get_parser(filename="prefs")


class _Config:
    def __init__(
        self,
        parser_factory: Callable[[], ConfigParser],
        section: str,
        key: str,
        default: Any,
    ):
        """Parent that sets logic for interacting with a key that returns a
        single value on a specific configuration file.

        :parser_factory: Function that always returns a `ConfigParser` with an attribute
          `_config_file` indicating the file to where this parser writes.
        :section: Name of the section where this config is located.
        :key: Name of this option in the config file.
        :default: Default value of this option, must be compatible with the input type
          of this class' `__set` method.
        """
        self._parser_factory, self._section, self._key, self._default = (
            parser_factory,
            section,
            key,
            default,
        )
        parser = self._parser_factory()
        if not parser.has_section(section):
            parser.add_section(section=section)
            with open(parser._config_file, "w") as configfile:
                parser.write(configfile)

    @classmethod
    def get(cls):
        """Get current value of this config, or the default value if not defined."""
        interactor = cls()
        print(interactor)
        return interactor.__get()

    @classmethod
    def set(cls, value: Any):
        """Write `value` to the configuration file."""
        interactor = cls()
        interactor.__set(value)

    def __set(self, value: Any):
        parser = self._parser_factory()
        parser.set(self._section, self._key, str(value))
        with open(parser._config_file, "w") as configfile:
            parser.write(configfile)

    def __get(self) -> Any | None:
        parser = self._parser_factory()
        try:
            return parser.get(self._section, self._key, fallback=self._default)
        except NoOptionError:
            self.__set(value=self._default)
            return self._default


class _ConfigList:
    def __init__(
        self,
        parser_factory: Callable[[], ConfigParser],
        section: str,
        key: str,
        default: list,
    ):
        """Parent that sets logic for interacting with a key that returns a
        list of values on a specific configuration file.

        :parser_factory: Function that always returns a `ConfigParser` with an attribute
          `_config_file` indicating the file to where this parser writes.
        :section: Name of the section where this config is located.
        :key: Name of this option in the config file.
        :default: Default value of this option, must be compatible with the input type
          of this class' `__set` method.
        """
        self._parser_factory, self._section, self._key, self._default = (
            parser_factory,
            section,
            key,
            default,
        )
        parser = self._parser_factory()
        if not parser.has_section(section):
            parser.add_section(section)
            with open(parser._config_file, "w") as configfile:
                parser.write(configfile)

    @classmethod
    def get(cls) -> list[Any]:
        """Get list from config file as a python list."""
        interactor = cls()
        return list(interactor.__get())

    @classmethod
    def set(cls, value: list):
        """Writes a a python list to the config file, replacing the existing one."""
        interactor = cls()
        interactor.__set(value=[str(i) for i in value])

    @classmethod
    def add(cls, value: str):
        """Adds a `value` to the config list."""
        interactor = cls()
        interactor.__add(value=value)

    @classmethod
    def rm(cls, value: str):
        """Removes `value` from config list if it is present. Does nothing otherwise."""
        interactor = cls()
        interactor.__rm(value=value)

    def __get(self) -> Iterator[str]:
        parser = self._parser_factory()
        try:
            string = parser.get(self._section, self._key)
            string = string.replace("[", "").replace("]", "")
            list_of_items = string.split(",")
        except NoOptionError:
            self.__set(value=self._default)
            list_of_items = self._default
        return (i.strip() for i in list_of_items if i.strip() != "")

    def __set(self, value: list[str]) -> str:
        string_list = (
            str(value)
            .replace("[", "[\n\t")
            .replace(", ", ",\n\t")
            .replace("'", "")
            .replace("]", "\n]")
            .replace("\\\\", "\\")
        )
        parser = self._parser_factory()
        parser.set(self._section, self._key, string_list)
        with open(parser._config_file, "w") as configfile:
            parser.write(configfile)

    def __add(self, value: str):
        current = [i for i in self.__get()]
        new = current + [value]
        self.__set(value=new)

    def __rm(self, value: str):
        current = [i for i in self.__get()]
        try:
            current.remove(value)
        except ValueError:
            return
        self.__set(value=current)


class BackupPlaces(_ConfigList):
    def __init__(self):
        super().__init__(
            parser_factory=get_default_parser,
            section="backup",
            key="backup_places",
            default=[],
        )
