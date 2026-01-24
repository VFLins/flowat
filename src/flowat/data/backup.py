from os import path, rename, makedirs
from sys import platform
from pathlib import Path
from datetime import datetime
import configparser
import sqlite3
import logging
import shutil

from .db import DB_FILE, DATA_PATH
from flowat import config


if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Flowat")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "configs")
    LOG_PATH = Path(FLOAT_FILES_PATH, "logs")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Cashd")
    CONFIG_PATH = Path.home().joinpath(".config", "Cashd")
    LOG_PATH = Path.home().joinpath(".local", "state", "Flowat", "log")

CONFIG_FILE = Path(CONFIG_PATH, "backup.ini")
LOG_FILE = Path(LOG_PATH, f"{__name__}.log")
BACKUP_PATH = Path(DATA_PATH, "backup")

for dirpath in [FLOWAT_FILES_PATH, CONFIG_PATH, LOG_PATH, BACKUP_PATH]:
    dirpath.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
loghandler = logging.FileHandler(filename=LOG_FILE, mode="a", encoding="utf-8")
loghandler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)
logger.setLevel(logging.DEBUG)



def copy_file(source_path: str, target_dir: str):
    """Copies a file to `target_dir`.

    :param source_path: Full path to the file to be copied.
    :param target_dir: Directory where the file will be copied into.
    """
    logger.debug("function call: copy_file")
    if not path.exists(target_dir):
        logger.error(f"Could not copy file to '{target_dir}', directory does not exist.")
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    try:
        filename = f"backup_{now}.db"
        shutil.copyfile(src=source_path, dst=Path(target_dir, filename))
        logger.info(f"Copy of '{source_path}' created at '{target_dir}'")
    except FileNotFoundError as err:
        logger.error(f"Error while copying file", exc_info=err)


def run() -> None:
    """Copies the database file to the local backup folder and to the folders listed in
    the 'backup_places' option in `backup.ini`.
    :param settings: Settings handler that will be used to read the database file's size.
    """
    backup_places: list = config.BackupPlaces.get()
    try:
        backup_places = [i for i in [BACKUP_PATH] + backup_places if i != ""]
        for place in backup_places:
            try:
                copy_file(DB_FILE, place)
                logger.info(f"Succesful backup to '{place}'")
            except Exception as err:
                logger.error(f"Could not backup to '{place}'", exc_info=err)
    except Exception as err:
        logger.error(f"Erro inesperado durante o backup", exc_info=err)
