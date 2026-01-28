from typing import Literal, Iterable
from sqlalchemy import Engine, Select, func, select, or_, text
from sqlalchemy.orm import Session
from copy import copy
import re

from .db import DB_ENGINE, ExpenseType, RevenueType, ExpenseEntry, RevenueEntry
from flowat import config


class _DataSource:
    def __init__(
        self,
        select_stmt: Select,
        paginated: bool = True,
        search_colnames: Iterable[str] = [],
        engine: Engine = DB_ENGINE,
    ):
        """Create a data class that interacts with the database, providing interaction
        capabilities to data widgets.

        :param select_stmt: A `sqlalchemy.sql.expression.Select` that selects the data
          managed by this data source.
        :param paginated: Wether this data source handle pagination.
        :param search_colnames: Name of the columns where the search will be applied.
        :param engine: Engine pointing to the database where the data will be handled.

        :raises ValueError: If `searchable=True`, and `search_colnames` is an empty list,
          or if one of the selected column names are not present in the select query.
        """
        selected_colnames = select_stmt.selected_columns.keys()
        for col in search_colnames:
            if col not in selected_colnames:
                raise ValueError(f"Expected all `search_colnames` to be present in {
                        selected_colnames
                    }.")
        self.SEARCH_COLNAMES = search_colnames
        if paginated:
            self._current_page = 1
            self._rows_per_page = config.PageSize.get()
        self.SELECT_STMT = select_stmt
        self.ENGINE = engine

    @property
    def search_text(self) -> str:
        """Text that should be used to apply search filters to this datasource."""
        if self.is_searchable() and hasattr(self, "_search_text"):
            return self._search_text
        else:
            return ""

    @search_text.setter
    def search_text(self, value: str):
        if self.is_searchable():
            self._search_text = str(value)

    @property
    def nrows(self) -> int:
        """Number of rows that should be returned by `current_data`."""
        with Session(self.ENGINE) as ses:
            select_stmt = self._get_searched_select_stmt(
                stmt=self.SELECT_STMT, search_text=self.search_text
            )
            nrows_stmt = select(func.count()).select_from(select_stmt.subquery())
            return ses.execute(nrows_stmt).scalar()

    @property
    def min_idx(self) -> int:
        """Index number of the first row currently displayed by this datasource."""
        if not self.is_paginated():
            return 0
        if self.nrows < self.rows_per_page:
            return 0
        else:
            return self.rows_per_page * (self.current_page - 1)

    @property
    def max_idx(self) -> int:
        """Index number of the last row currently displayed by this datasource."""
        max_idx = self.current_page * self.rows_per_page
        if self.nrows < max_idx:
            return self.nrows
        else:
            return max_idx

    @property
    def sort_ascending(self) -> bool:
        """Indicates if the sorting should be performed in ascending order."""
        return getattr(self, "_sort_ascending", True)

    @sort_ascending.setter
    def sort_ascending(self, value: bool):
        self._sort_ascending = bool(value)

    @property
    def sort_column(self) -> str:
        """Column name of the column where the sorting should be performed."""
        colname = getattr(self, "_sort_column", None)
        if colname in self.column_names:
            return colname
        return self.column_names[0]

    @sort_column.setter
    def sort_column(self, value: str):
        if value in self.column_names:
            self._sort_column = str(value)
        else:
            raise ValueError(
                f"`sort_column` should be one of {self.column_names}, not '{value}'."
            )

    @property
    def column_names(self) -> tuple[str]:
        """Column names returned by this datasource's select statement."""
        return tuple(self.SELECT_STMT.columns.keys())

    @property
    def current_data(self) -> list:
        """Assigns the data based on the current metadata values to
        `current_data`.
        """
        stmt = self._get_searched_select_stmt(
            stmt=self.SELECT_STMT, search_text=self.search_text
        )
        stmt = self._get_sorted_select_stmt(
            stmt=stmt,
            colname=self.sort_column,
            ascending=self.sort_ascending,
        )
        if self.is_paginated():
            stmt = stmt.limit(self.rows_per_page).offset(self.min_idx)
        with Session(self.ENGINE) as ses:
            return ses.execute(stmt).all()

    def get_data_slice(self, irange: tuple[int, int] | None = None) -> list:
        """Generator containing all rows of this source, or a range of indexes.
        The idexes follow the same as Python's.
        """
        stmt = self.SELECT_STMT
        reverse = False
        if irange:
            first, last = irange
            if last < first:
                first, last = last, first
                reverse = True
            stmt = stmt.limit(last - first).offset(first)
        with Session(self.ENGINE) as ses:
            result = ses.execute(stmt).all()
            if reverse:
                return list(reversed(result))
            return result

    def is_paginated(self) -> bool:
        try:
            _ = self._current_page
            return True
        except AttributeError:
            return False

    def is_searchable(self) -> bool:
        try:
            _ = self._search_text
            return True
        except AttributeError:
            return False

    def _get_searched_select_stmt(self, stmt: Select, search_text: str = "") -> Select:
        """If this is a searchable data source, adds a search logic to `stmt` and
        returns it. Returns only `stmt` otherwise, or if `search_text` is an empty
        string.

        :param search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.
        """
        stmt_copy = copy(stmt)
        keywords = re.findall(r"\w+", search_text)
        for kw in keywords:
            kw_in_cols = [
                self.SELECT_STMT.selected_columns[col].ilike(f"%{kw}%")
                for col in self.SEARCH_COLNAMES
            ]
            stmt_copy = stmt_copy.where(or_(*kw_in_cols))
        return stmt_copy

    def _get_sorted_select_stmt(
        self, stmt: Select, colname: str, ascending: bool = True
    ) -> Select:
        """Adds a sort logic to `stmt` and returns it. If this source is not sortable
        or colname cannot be found, returns `stmt` with no modifications.

        :param colname: Column name defined in `self.SELECT_STMT`.
        :param ascending: Indicates if sorting should be ascending or not.
        """
        stmt_copy = copy(stmt)
        self.sort_ascending = ascending
        self.sort_column = colname
        sortby = [
            col for col in stmt_copy.selected_columns if col.name == self.sort_column
        ][0]
        return stmt_copy.order_by(
            sortby.asc() if self.sort_ascending else sortby.desc()
        )

    @property
    def current_page(self) -> int:
        """Current page number."""
        if not self.is_paginated():
            return 1
        return self._current_page

    @property
    def rows_per_page(self) -> int:
        """Maximum number of rows per page in any datasource."""
        return config.PageSize.get()

    def fetch_next_page(self):
        """Advances one page and update `current_data`. Does nothing if already
        on last page.
        """
        if self.max_idx == self.nrows:
            return
        self._current_page = self._current_page + 1

    def fetch_previous_page(self):
        """Backtracks one page and update `current_data`. Does nothing if already
        on first page.
        """
        if self._current_page == 1:
            return
        self._current_page = self._current_page - 1

    def update_date_format(self, date_freq: Literal["m", "w", "d"]):
        """Updates `self.SELECT_STMT` to reflect the date frequency requested. Does
        nothing if the data source can't accept date frequency updates.
        """
        raise NotImplementedError()


class ExpenseTypeSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        super().__init__(
            select_stmt=select(ExpenseType.Id, ExpenseType.Name),
            paginated=False,
            engine=engine,
        )


class RevenueTypeSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        super().__init__(
            select_stmt=select(RevenueType.Id, RevenueType.Name),
            paginated=False,
            engine=engine,
        )


class ExpensesSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        stmt = select(
            ExpenseEntry.Id,
            ExpenseType.Name.label("TransactionType"),
            ExpenseEntry.Description,
            ExpenseEntry.TransactionDate,
            ExpenseEntry.TransactionValue,
        ).join(ExpenseEntry, ExpenseEntry.IdExpenseType == ExpenseType.Id)
        super().__init__(
            select_stmt=stmt,
            paginated=True,
            search_colnames=[
                "TransactionType",
                "Description",
                "TransactionDate",
                "TransactionValue",
            ],
            engine=engine,
        )
