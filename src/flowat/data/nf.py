from sqlalchemy import create_engine, Engine, inspect, select, Table, MetaData
from sqlalchemy.orm import Session
from typing import Generator
import pandas as pd
import nflogic

from flowat.data import db

NFLOGIC_ENGINE = create_engine(f"sqlite:///{nflogic.db.DB_PATH}", echo=False)


class TableName:
    def __init__(self, table_name: str):
        self._table_name = table_name

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def display_name(self) -> str:
        return (
            self.table_name.replace("VENDA_", "")
            .replace("COMPRA_", "")
            .replace("_", " ")
            .title()
        )


def _get_table_by_name(table_name: str, engine: Engine) -> Table:
    """Returns a `sqlalchemy.Table` object from name and engine."""
    meta = MetaData()
    return Table(name=table_name, metadata=meta, autoload_with=engine)


def read_flowat_revenues(engine: Engine = db.DB_ENGINE) -> pd.DataFrame:
    """Reads data from flowat's database to get all documents already scanned."""
    with Session(engine) as ses:
        stmt = (
            select(
                db.ScannedInvoiceFile.Id,
                db.ScannedInvoiceFile.DocumentIdentifier,
                db.RevenueEntry.TimeStamp,
                db.RevenueEntry.Description,
                db.RevenueEntry.TransactionDate,
                db.RevenueEntry.TransactionValue,
            )
            .where(db.RevenueEntry.Id == db.ScannedInvoiceFile.IdRevenueEntry)
            .join(
                db.ScannedInvoiceFile,
                db.RevenueEntry.Id == db.ScannedInvoiceFile.IdRevenueEntry,
            )
        )
        res = ses.execute(stmt)
        return pd.DataFrame(data=res, columns=[c.name for c in stmt.selected_columns])


def read_nflogic_revenues(
    seller_name: TableName, engine: Engine = NFLOGIC_ENGINE
) -> pd.DataFrame:
    """Reads data from nflogic's database to get all documents already scanned."""
    table = _get_table_by_name(table_name=seller_name.table_name, engine=engine)
    with Session(engine) as ses:
        stmt = select(
            table.c.Id,
            table.c.ChaveNFe,
            table.c.DataHoraEmi,
            table.c.TotalProdutos,
        )
        res = ses.execute(stmt)
        return pd.DataFrame(data=res, columns=[c.name for c in stmt.selected_columns])


def get_seller_names(engine: Engine = NFLOGIC_ENGINE) -> list[TableName]:
    """Get a list of seller names formatted in title case."""
    insp = inspect(engine)
    return [
        TableName(table_name=name)
        for name in insp.get_table_names()
        if name[:6] == "VENDA_"
    ]


def get_new_seller_data(
    seller_name: TableName,
    internal_engine: Engine = db.DB_ENGINE,
    nf_engine: Engine = NFLOGIC_ENGINE,
) -> Generator[tuple, None, None]:
    """Get a list of rows collected from nflogic's database that is not present in a
    flowat table.
    """
    nflogic_df = read_nflogic_revenues(seller_name=seller_name)
    flowat_df = read_flowat_revenues()
    new_data = nflogic_df.loc[
        ~nflogic_df["ChaveNFe"].is_in(flowat_df["DocumentIdentifier"])
    ]
