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
    def __init__(self, parser: ConfigParser, section: str, key: str, default: Any | None):
        """Parent metaclass that sets logic for interacting with a single key on a
        specific configuration file.
        """
        self._parser, self._section, self._key, self._default = (
            parser, section, key, default
        )
        if not parser.has_section(section):
            parser.add_section(section=section)

    def _refresh(self):
        self._parser.read(self._parser._config_file)

    def set(self, value: Any):
        self._parser.set(self._section, self._key, str(value))

    def get() -> Any:
        self._refresh()
        return self._parser.get(self._section, self._key, fallback=self._default)


class BackupPlaces(_Config):
    def __init__(self):
        super().__init__(
            parser=get_default_parser(),
            section="backup",
            key="backup_places",
            default=None,
        )


def get(interactor: _Config) -> Any:
    """Refresh the parser with the current data and return the expected value."""
    config_obj = interactor()
    return interactor.get()


def set(interactor: _Config, value: Any):
    """Write `value` to the configuration file."""
    config_obj = interactor()
    config_obj.set(value)
