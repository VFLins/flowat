from os import path, rename, makedirs
from sys import platform
from pathlib import Path
from datetime import datetime
import configparser
import sqlite3
import logging
import shutil

from .db import DB_FILE


if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Cashd")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "configs")
    LOG_PATH = Path(FLOAT_FILES_PATH, "logs")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Cashd")
    CONFIG_PATH = Path.home().joinpath(".config", "Cashd")
    LOG_PATH = Path.home().joinpath(".local", "state", "Cashd", "logs")

CONFIG_FILE = Path(CONFIG_PATH, "backup.ini")
LOG_FILE = path.join(LOG_PATH, "backup.log")
BACKUP_PATH = path.join(FLOWAT_FILES_PATH, "data", "backup")

for dirpath in [CASHD_FILES_PATH, CONFIG_PATH, LOG_PATH, BACKUP_PATH]:
    makedirs(dirpath, exist_ok=True)


def run(settings: BackupPrefsHandler = settings) -> None:
    """Copies the database file to the local backup folder and to the folders listed in
    the 'backup_places' option in `backup.ini`.
    :param settings: Settings handler that will be used to read the database file's size.
    """
    backup_places: list = settings.read_backup_places()
    error_was_raised = False

    current_size = read_db_size()
    previous_size = settings.read_dbsize()

    if not force:
        if current_size <= previous_size:
            return
    settings.write_dbsize(current_size)

    try:
        backup_places = [i for i in [BACKUP_PATH] + backup_places if i != ""]
        for place in backup_places:
            try:
                copy_file(DB_FILE, place, _raise=_raise)
            except Exception as err:
                logger.error(
                    f"Nao foi possivel salvar em '{place}': {err}", exc_info=True
                )
                if _raise:
                    error_was_raised = True
    except Exception as err:
        logger.error(f"Erro inesperado durante o backup: {err}", exc_info=True)
    finally:
        if error_was_raised:
            raise NotADirectoryError(
                f"Erro em alguma etapa do backup, verifique o log: {LOG_FILE}"
            )
