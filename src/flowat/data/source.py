from typing import Literal, Iterable
from sqlalchemy import Engine, Select, func, select, or_
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
        serchable = bool(len(search_colnames))
        sortable = bool(len(sort_colnames))
        selected_colnames = select_stmt.selected_columns.keys()
        for col in search_colnames:
            if col not in selected_colnames:
                raise ValueError(
                    f"Expected all `search_colnames` to be present in {
                        selected_colnames
                    }."
                )
        if paginated:
            self._current_page = 1
            self._rows_per_page = config.PageSize.get()
        if searchable:
            self._search_text = ""
            self.SEARCH_COLNAMES = search_colnames
        self.SELECT_STMT = select_stmt
        self.ENGINE = engine
        self._fetch_metadata()

    def _fetch_metadata(self, search_text: str = ""):
        """Assigns values for attributes containing metadata for the current
        state of this class's `select_statement`:

        - :nrows: Number of rows in this data source. Affected by search text
          when the data source is searchable.

        If searchable:

        - :search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.

        If paginated:

        - :min_idx: Index of the first item in the current page;
        - :max_idx: Index of the last item in the current page.
        """
        # `search_text`
        if self.is_searchable():
            self._search_text = search_text
        # `nrows`
        with Session(self.ENGINE) as ses:
            select_stmt = self.searched_select_stmt(
                stmt=self.SELECT_STMT,
                search_text=search_text
            )
            nrows_stmt = select(func.count()).select_from(select_stmt.subquery())
            self.nrows = ses.execute(nrows_stmt).scalar()
        if self.is_paginated():
            # `min_idx`
            if self.nrows < self._rows_per_page:
                self.min_idx = 0
            else:
                self.min_idx = self._rows_per_page * (self.current_page - 1)
            # `max_idx`
            max_idx = self.current_page * self._rows_per_page
            if self.nrows < max_idx:
                self.max_idx = self.nrows
            else:
                self.max_idx = max_idx

    @property
    def current_data(self) -> list:
        """Assigns the data based on the current metadata values to
        `current_data`.
        """
        stmt = self.searched_select_stmt(
            stmt=self.SELECT_STMT,
            search_text=self.search_text
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

    def searched_select_stmt(self, stmt: Select, search_text: str = "") -> Select:
        """If this is a searchable data source, adds a search logic to `stmt` and
        returns it. Returns only `stmt` otherwise, or if `search_text` is an empty
        string.

        :param search_text: Text with all the keywords that will be inserted into the
          searched SELECT query.
        """
        stmt_copy = copy(stmt)
        if not self.is_searchable() or (search_text == ""):
            return stmt_copy
        keywords = re.findall(r"\w+", search_text)
        for kw in keywords:
            kw_in_cols = [
                self.SELECT_STMT.selected_columns[col].ilike(f"%{kw}%")
                for col in self.SEARCH_COLNAMES
            ]
            stmt_copy = stmt_copy.where(or_(*kw_in_cols))
        return stmt_copy

    def sorted_select_stmt(self, stmt: Select, colname: str, ascending: bool = True) -> Select:
        """Adds a sort logic to `stmt` and returns it. If this source is not sortable
        or colname cannot be found, returns `stmt` with no modifications.

        :param colname: Column name defined in `self.SELECT_STMT`.
        :param ascending: Indicates if sorting should be ascending or not.
        """
        stmt_copy = copy(stmt)
        if not self.is_sortable() or (colname not in self.SORT_COLNAMES):
            return stmt_copy
        return stmt_copy.order_by(text(f"{colname} {'ASC' if ascending else 'DESC'}"))

    @property
    def current_page(self) -> int:
        """Current page number."""
        if not self.is_paginated():
            raise AttributeError(
                "Cannot get 'current_page' on a data source without pagination."
            )
        return self._current_page

    @property
    def rows_per_page(self) -> int:
        self._rows_per_page = config.PageSize.get()
        return self._rows_per_page

    def fetch_next_page(self):
        """Advances one page and update `current_data`. Does nothing if already
        on last page.
        """
        if self.max_idx == self.nrows:
            return
        self._current_page = self._current_page + 1
        self._fetch_metadata()

    def fetch_previous_page(self):
        """Backtracks one page and update `current_data`. Does nothing if already
        on first page.
        """
        if self._current_page == 1:
            return
        self._current_page = self._current_page - 1
        self._fetch_metadata()

    def update_date_format(self, date_freq: Literal["m", "w", "d"]):
        """Updates `self.SELECT_STMT` to reflect the date frequency requested. Does
        nothing if the data source can't accept date frequency updates, or if `date_freq`
        is not one of ['m', 'w', 'd'].
        """
        pass

    @property
    def search_text(self) -> str:
        """If searchable, returns the last provided `search_text`, or an empty
        string otherwise.
        """
        return getattr(self, "_search_text", "")

    @search_text.setter
    def search_text(self, value: str):
        if self.is_searchable():
            self._fetch_metadata(search_text=value)


class ExpenseTypeSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        super().__init__(
            select_stmt=select(ExpenseType.Id, ExpenseType.Name),
            paginated=False,
            engine=engine
        )


class RevenueTypeSource(_DataSource):
    def __init__(self, engine: Engine = DB_ENGINE):
        super().__init__(
            select_stmt=select(RevenueType.Id, RevenueType.Name),
            paginated=False,
            engine=engine
        )

class ExpensesSource(_DataSource):
    def __init(self, engine: Engine = DB_ENGINE):
        stmt = select(
            ExpenseEntry.Id,
            RevenueType.Name.label("TransactionType"),
            ExpenseEntry.Description,
            ExpenseEntry.TransactionDate,
            ExpenseEntry.TransactionValue,
        ).join(RevenueType)
        super().__init__(
            select_stmt=stmt,
            paginated=True,
            =["Adicionado", "Vencimento"]
        )
