from datetime import date
from dateutil.relativedelta import relativedelta

from toga.widgets.numberinput import NumberInput
from toga.widgets.selection import Selection
from toga.widgets.box import Row, Column
from toga.style import Pack

from flowat.const import style
from flowat.form.elem import FormField


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
        self.year_container = FormField(
            label="Ano",
            input_widget=NumberInput(min=1, max=9999, value=value.year),
        )
        self.month_container = FormField(
            label="Mês",
            input_widget=Selection(
                items=self.MONTHS,
                value=self.MONTHS[value.month - 1],
                on_change=self._update_allowed_day_values,
            ),
        )
        self.day_container = FormField(
            label="Dia",
            input_widget=NumberInput(
                min=1, max=self._last_day_of_month(), value=value.day
            ),
        )
        self.widget = Row(
            id=id,
            children=[self.day_container, self.month_container, self.year_container],
        )

    @property
    def value(self):
        return date(
            int(self.year_container.input.value),
            self._month_number(),
            int(self.day_container.value),
        )

    @value.setter
    def value(self, value: date):
        self.day_container.input.value = value.day
        self.month_container.input.value = self.MONTHS[value.month - 1]
        self.year_container.input.value = value.year

    def _last_day_of_month(self) -> int:
        year, month = int(self.year_container.input.value), self._month_number()
        return int((date(year, month, 1) + relativedelta(day=31)).day)

    def _update_allowed_day_values(self, widget):
        max_day = self._last_day_of_month()
        if self.day_container.input.value > max_day:
            self.day_container.input.value = max_day
        self.day_container.input.max = max_day

    def _month_number(self) -> int:
        """Returns the month number 1-12 of the currently selected month."""
        month_name = self.month_container.input.value
        return int(self.MONTHS.index(month_name) + 1)


class VerticalDateForm(HorizontalDateForm):
    def __init__(self, value: date, id: str | None = None):
        super().__init__(id=id, value=value)
        self.widget = Column(
            id=id,
            children=[
                self.day_container,
                self.month_container,
                self.year_container,
            ],
        )
