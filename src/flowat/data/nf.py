from sqlalchemy import (
    create_engine,
    Engine,
    inspect,
    insert,
    select,
    exists,
    not_,
    Table,
    MetaData,
    func,
    text,
    Column,
    String,
)
from sqlalchemy.orm import Session
from contextlib import contextmanager
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
            .upper()
        )

    def __str__(self):
        return self.display_name


def _get_table_by_name(table_name: str, engine: Engine) -> Table:
    """Returns a `sqlalchemy.Table` object from name and engine."""
    meta = MetaData()
    return Table(table_name, meta, autoload_with=engine)


def _get_registered_document_identifiers(
    engine: Engine = db.DB_ENGINE,
) -> list[str]:
    """Returns a list of document identifiers registered in Flowat's database."""
    with Session(engine) as ses:
        stmt = select(db.ScannedInvoiceFile.DocumentIdentifier)
        res = ses.execute(stmt)
        return [r.DocumentIdentifier for r in res]


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


@contextmanager
def _set_temporary_table(*columns: Column, metadata: MetaData, engine: Engine) -> Table:
    try:
        TMP_TABLE = Table(
            "FLOWAT_TEMPORARY",
            metadata,
            *columns,
            prefixes=["TEMPORARY"],
        )
        TMP_TABLE.create(bind=engine, checkfirst=True)
        yield TMP_TABLE
    finally:
        TMP_TABLE.drop(bind=engine, checkfirst=True)


def get_new_seller_data(
    seller_name: TableName,
    internal_engine: Engine = db.DB_ENGINE,
    nf_engine: Engine = NFLOGIC_ENGINE,
) -> Generator[tuple, None, None]:
    """Get a list of rows collected from nflogic's database that is not present in a
    flowat table.
    """
    registered_docs = _get_registered_document_identifiers(engine=internal_engine)
    NF_TABLE = _get_table_by_name(table_name=seller_name.table_name, engine=nf_engine)
    # NOTE: use temporary table INSERT to avoid using a SELECT statement with a large
    # NOT IN clause
    with Session(bind=nf_engine) as ses:
        with _set_temporary_table(
            Column("DocId", String, primary_key=True),
            metadata=NF_TABLE.metadata,
            engine=nf_engine,
        ) as TMP_TABLE:
            if registered_docs:
                ses.execute(insert(TMP_TABLE), [{"DocId": i} for i in registered_docs])
            stmt = select(
                NF_TABLE.c.Id,
                TMP_TABLE.c.DocId,
                NF_TABLE.c.DataHoraEmi,
                NF_TABLE.c.TotalProdutos,
            ).join(TMP_TABLE, NF_TABLE.c.ChaveNFe == TMP_TABLE.c.DocId)
            res = ses.execute(stmt)
            return res


def count_new_seller_data(
    seller_name: TableName,
    internal_engine: Engine = db.DB_ENGINE,
    nf_engine: Engine = NFLOGIC_ENGINE,
) -> int:
    """Get a list of rows collected from nflogic's database that is not present in a
    flowat table.
    """
    registered_docs = _get_registered_document_identifiers(engine=internal_engine)
    NF_TABLE = _get_table_by_name(table_name=seller_name.table_name, engine=nf_engine)
    with Session(bind=nf_engine) as ses:
        with _set_temporary_table(
            Column("DocId", String, primary_key=True),
            metadata=NF_TABLE.metadata,
            engine=nf_engine,
        ) as TMP_TABLE:
            if registered_docs:
                ses.execute(insert(TMP_TABLE), [{"DocId": i} for i in registered_docs])
            stmt = select(func.count(NF_TABLE.c.ChaveNFe)).where(
                not_(exists().where(TMP_TABLE.c.DocId == NF_TABLE.c.ChaveNFe))
            )
            res = ses.execute(stmt)
            return res.scalar_one()


def get_seller_names(engine: Engine = NFLOGIC_ENGINE) -> list[TableName]:
    """Get a list of seller names formatted in title case."""
    insp = inspect(engine)
    return [
        TableName(table_name=name)
        for name in insp.get_table_names()
        if name[:6] == "VENDA_"
    ]
