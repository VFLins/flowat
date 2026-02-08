from typing import Callable, Type
from sys import platform

from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Row, Column
from toga.style import Pack

from flowat.const import style
from flowat.data import db


class InputPaginator:
    def __init__(
        self,
        data: Type[db.DeclaredTable] | None = None,
        n_pages: int = 1,
        pagination_label: str = "",
        on_page_change: Callable[[], None] | None = None,
    ):
        """Assigns a `toga.Box` with pagination widgets to it's `widget` property.
        Helps handling on muliple different input data in the same form.

        :data: Initial input of all pages.
        :n_pages: Initial amount of input sets handled.
        :pagination_label: Text displayed in the pagination widgets.
        :on_page_change: Callable indicating actions to be performed when the user
            interacts with any pagination widget.
        """
        if data is not None:
            self._data = [data for i in range(n_pages)]
        else:
            self._data = [{}]
        self._pagination_label = pagination_label
        if on_page_change is not None:
            self._on_page_change = on_page_change
        self._current_page = 1
        self._current_data = self._data[0]
        self.pagination_label = Label(f"{pagination_label} 1/{n_pages}")
        self.next_page_button = Button(
            "→", style=style.RIGHTMOST_SIMPLE_SMALL_BUTTON, on_press=self.set_next_page
        )
        self.previous_page_button = Button(
            "←", style=style.SIMPLE_SMALL_BUTTON, on_press=self.set_previous_page
        )
        self.pagination_widget = Row(
            style=Pack(align_items="center"),
            children=[
                self.pagination_label,
                self.previous_page_button,
                self.next_page_button,
            ],
        )
        self.placeholder_widget = Row(
            style=Pack(height=38 if platform == "linux" else 28)
        )
        self.widget = Column(
            style=Pack(width=style.FORM_WIDTH, align_items="end"),
            children=[self.placeholder_widget],
        )

    @property
    def current_data(self) -> Type[db.DeclaredTable] | None:
        return getattr(self, "_current_data", None)

    @current_data.setter
    def current_data(self, value: Type[db.DeclaredTable]):
        self._current_data = value
        self._data[self._current_page - 1] = value

    @property
    def on_page_change(self) -> Callable[[], None]:
        def no_op():
            return

        return getattr(self, "_on_page_change", no_op)

    @on_page_change.setter
    def on_page_change(self, value: Callable[[], None]):
        self._on_page_change = value

    @property
    def n_pages(self) -> int:
        return len(self._data)

    def _update_state(self):
        self.pagination_label.text = (
            f"{self._pagination_label} {self._current_page}/{self.n_pages}"
        )
        self._current_data = self._data[self._current_page - 1]
        if self.n_pages > 1:
            self.widget.remove(self.placeholder_widget)
            self.widget.add(self.pagination_widget)
        else:
            self.widget.remove(self.pagination_widget)
            self.widget.add(self.placeholder_widget)

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
        self.on_page_change()

    def set_next_page(self, widget: Button | None = None):
        self.set_page(n=self._current_page + 1)

    def set_previous_page(self, widget: Button | None = None):
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
