from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Any

from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Row, Column
from toga.style import Pack

from flowat.const import style
from flowat.form.elem import FormField


class InputPaginator:
    def __init__(self, data: dict[str, Any] | None = None, n_pages: int = 1):
        """Assigns a `toga.Box` with pagination widgets to it's `widget` property.
        Helps handling on muliple different input data in the same form.

        :data: Initial input of all pages.
        :n_pages: Initial amount of input sets handled.
        """
        if data is not None:
            self._data = [data for i in range(n_pages)]
        else:
            self._data = [{}]
        self._current_page = 1
        self._current_data = self._data[0]
        self.pagination_label = Label(f"1/{n_pages}")
        self.next_page_button = Button("próximo", style=style.SIMPLE_SMALL_BUTTON)
        self.previous_page_button = Button("anterior", style=style.SIMPLE_SMALL_BUTTON)
        self.widget = Row(
            style=Pack(align_items="center"),
            children=[
                self.pagination_label,
                self.previous_page_button,
                self.next_page_button,
            ]
        )

    @property
    def current_data(self) -> dict:
        return dict(getattr(self, "_current_data", {}))

    @property
    def n_pages(self) -> int:
        return len(self._data)

    def _update_state(self):
        self.pagination_label.text = f"{self._current_page}/{self.n_pages}"
        self._current_data = self._data[self._current_page - 1]

    def set_page(self, n: int):
        """Updates current page data and pagination label accordingly. Will set last
        available page if `n` is greater than the current page amount, or first if
        smaller than zero.
        """
        if n > self.n_pages:
            self._current_page = self.n_pages
        elif n < 1:
            self._current_page = 1
        else:
            self._current_page = n
        self._update_state()

    def set_next_page(self):
        self.set_page(n=self._curent_page + 1)

    def set_previous_page(self):
        self.set_page(n=self._current_page - 1)

    def set_page_amount(self, n: int):
        """Change the amount of pages to a specific number. When increasing, will
        replicate the data from the last page to the newly created ones, when
        decreasing, will remove the last pages.
        """
        if n > self.n_pages:
            last_page_data = self._data[len(self._data) - 1]
            n_created = int(n - self.n_pages)
            self._data = self._data + [last_page_data for d in range(n_created)]
        else:
            self._data = self._data[:n]
        self.set_page(n=min(self._current_page, self.n_pages))


