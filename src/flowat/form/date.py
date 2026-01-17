from math import ceil
from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Type, Iterable, Callable

from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.base import Widget
from toga.widgets.numberinput import NumberInput
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.box import Box, StyleT
from toga.widgets.label import Label

from flowat.const import style
from flowat.form.elem import (
    LabeledSelection,
    LabeledNumberInput,
)

class HorizontalDateForm:
    MONTHS = (
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    )

    def __init__(self, value: date = date.today(), id: str | None = None):

        self.year_input = LabeledNumberInput(
            label_text="Ano",
            style=style.user_input(NumberInput),
            min=1,
            max=9999,
            value=value.year,
        )

        self.month_input = LabeledSelection(
            label_text="Mês",
            style=style.user_input(Selection),
            items=self.MONTHS,
            value=self.MONTHS[value.month - 1],
            on_change=self._update_allowed_day_values,
        )

        self.day_input = LabeledNumberInput(
            label_text="Dia",
            style=style.user_input(NumberInput),
            min=1,
            max=self._last_day_of_month(),
            value=value.day,
        )

        self.widget = Column(
            id=id,
            children=[
                self.day_input.widget,
                self.month_input.widget,
                self.year_input.widget,
            ],
        )

    @property
    def value(self):
        return date(
            int(self.year_input.value), self._month_number(), int(self.day_input.value)
        )

    @value.setter
    def value(self, value: date):
        self.day_input.value = value.day
        self.month_input.value = self.MONTHS[value.month - 1]
        self.year_input.value = value.year

    def _last_day_of_month(self) -> int:
        year, month = int(self.year_input.value), self._month_number()
        return int((date(year, month, 1) + relativedelta(day=31)).day)

    def _update_allowed_day_values(self, widget):
        max_day = self._last_day_of_month()
        if self.day_input.value > max_day:
            self.day_input.value = max_day
        self.day_input.max = max_day

    def _month_number(self) -> int:
        """Returns the month number 1-12 of the currently selected month."""
        month_name = self.month_input.value
        return int(self.MONTHS.index(month_name) + 1)


class VerticalDateForm(HorizontalDateForm):
    def __init__(self, value: date, id: str | None = None):
        super().__init__(id=id, value=value)
        self.widget = Row(
            id=id,
            children=[
                self.day_input.widget,
                self.month_input.widget,
                self.year_input.widget,
            ],
        )

