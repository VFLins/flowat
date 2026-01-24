from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Select,
    create_engine,
    DateTime,
    Date,
    Numeric,
    Integer,
    String,
    cast,
    update,
    select,
    insert,
    delete,
    or_,
    case,
    text,
    func,
    types,
)
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    relationship,
    Session,
)
from typing import List, Iterable, Literal, Any, Self, Dict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from copy import copy
from sys import platform
import re


if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Cashd")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "configs")
    LOG_PATH = Path(FLOWAT_FILES_PATH, "logs")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Cashd")
    CONFIG_PATH = Path.home().joinpath(".config", "Cashd")
    LOG_PATH = Path.home().joinpath(".local", "state", "Cashd", "logs")

DATA_PATH = Path(FLOWAT_FILES_PATH, "data")
DATA_PATH.mkdir(exist_ok=True)
DB_FILE = Path(DATA_PATH, 'database.db')
DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)

# VALIDATION
####################


class RequiredText(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_text(value, required=True)

    def process_result_value(self, value, dialect):
        return value


class NotRequiredText(types.TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_text(value, required=False)

    def process_result_value(self, value, dialect):
        return value


class CurrencyAmount(types.TypeDecorator):
    impl = Numeric
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return fmt_currency(value)

    def process_result_value(self, value, dialect):
        if value:
            return round(Decimal(value), 2)


REQUIRED_TYPES = [RequiredText]


def fmt_text(inp: str | None, required: bool = False) -> str:
    """Coerces input into a title cased string.

    :param inp: Input value
    :param required: Boolean value indicating if it is allowed to be empty.
    :raises ValueError: If it cannot be coerced to expected format.
    """
    if inp is None:
        inp = ""
    if required and (len(inp) == 0):
        raise ValueError("Campo obrigatório não pode ficar vazio")
    return inp.title()


def fmt_currency(inp: Any) -> int:
    """Coerces input into a non-zero integer value used to store currency in db.

    :param inp: Input value
    :raises ValueError: If it cannot be coerced to expected format.
    """
    if isinstance(inp, (str)):
        inp = inp.replace(",", "").replace(".", "")
    if isinstance(inp, (Decimal, float)):
        inp = inp * 100
    return int(inp)


class dec_base(DeclarativeBase):
    Id = Column("Id", Integer, primary_key=True)

    @staticmethod
    def _display_name(name: str):
        """Wrapper to generate the *display name* of any data scalar in `self.data`."""
        return name

    def table_is_empty(self, engine: Engine = DB_ENGINE):
        """Static method that returns a boolean value indicating if the current table
        is empty. Should only be used by classes that inherit from
        `cashd_core.data.dec_base`.
        """
        table_cls = type(self)
        with Session(engine) as ses:
            stmt = select(func.count()).select_from(table_cls)
            return ses.execute(stmt).scalar() == 0

    @property
    def data(self) -> dict[str, Any]:
        return {
            colname: getattr(self, colname, None)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    @property
    def display_names(self) -> dict[str, Any]:
        return {
            colname: self._display_name(colname)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    @property
    def types(self) -> dict[str, Any]:
        return {
            colname: type(self.__table__.c[colname].type)
            for colname in self.__table__.c.keys()
            if colname != "Id"
        }

    @property
    def required_fieldnames(self) -> List[str]:
        """Names of every required fields in this table."""
        return [
            colname for colname in self.data.keys()
            if self.types[colname] in REQUIRED_TYPES
        ]

    def required_fields_are_filled(self) -> bool:
        """Returns a boolean value indicating if all required fields for this table
        are filled.
        """
        return all(getattr(self, col) for col in self.required_fieldnames)

    def read(self, row_id: int, engine: Engine = DB_ENGINE):
        """
        Fetches one row of data from the database and loads into this instance.

        :param row_id: Primary key integer value to look for in the table.
        :param engine: `sqlalchemy.Engine` reflecting the database that will be read.

        :raises ValueError: If `row_id` is not present in the table.
        """
        cls = type(self)
        stmt = select(cls).where(cls.Id == row_id)
        with Session(bind=engine) as ses:
            res = ses.execute(stmt).first()
            if res is None:
                raise ValueError(
                    f"{row_id=} not present in '{
                        self.__tablename__}.Id'."
                )
            row = res[0]
            for col in self.__table__.columns:
                value = getattr(row, col.name, None)
                setattr(self, col.name, value)

    def clear(self):
        """Returns all dataclass fields to their defaults, and `Id=None`."""
        self.Id = None
        for name in self.data.keys():
            default_value = self.__table__.c[name].default
            setattr(self, name, default_value)

    def fill(self, tbl_obj: Self):
        """Fills own mapped columns with the custom values provided by `tbl_obj`."""
        self.Id = tbl_obj.Id
        for name, value in tbl_obj.data.items():
            setattr(self, name, value)

    def update(self, engine: Engine = DB_ENGINE):
        """If `self.Id` is defined, validates and updates the corresponding row in the
        database with it's own values.

        :raises AttributeError: If `self.Id` is None or not defined.
        """
        if not self.Id:
            raise AttributeError(
                f"Expected `self.Id` to be integer, got {self.Id=}.")
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = update(cls).where(cls.Id == self.Id).values(**self.data)
            ses.execute(stmt)
            ses.commit()
        self.read(row_id=self.Id, engine=engine)

    def write(self, engine: Engine = DB_ENGINE):
        """Validates and adds a new row in the database with it's own data."""
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = insert(cls).values(**self.data)
            ses.execute(stmt)
            ses.commit()

    def delete(self, engine: Engine = DB_ENGINE):
        """If `self.Id` is present in the database, attempts to delete it.

        :raises AttributeError: If `self.Id` is None or not defined.
        :raises sqlalchemy.exc.IntegrityError: If this deletion would leave orphaned
          foreign keys.
        """
        cls = type(self)
        with Session(bind=engine) as ses:
            stmt = delete(cls).where(cls.Id == self.Id)
            ses.execute(stmt)
            ses.commit()

