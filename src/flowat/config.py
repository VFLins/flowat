from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
    DuplicateSectionError
)
from pathlib import Path
from sys import platform
from os import makedirs


if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Flowat")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "config")
    LOG_PATH = Path(FLOWAT_FILES_PATH, "log")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Flowat")
    CONFIG_PATH = Path.home().joinpath(".config", "Flowat")
    LOG_PATH = Path.home().joinpath(".local", "state", "Flowat", "log")

for dir in [FLOWAT_FILES_PATH, CONFIG_PATH, LOG_PATH]:
    makedirs(dir, exist_ok=True)


class ConfigInterface:
    # https://stackoverflow.com/a/31909086
    def get_parser(self, filename: str) -> ConfigParser:
        parser = ConfigParser()
        parser.read(Path(CONFIG_PATH, f"{filename}.ini"))
        return parser

