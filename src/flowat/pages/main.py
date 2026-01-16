from toga.widgets.label import Label
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.box import Box, Column, Row
from toga.widgets.optioncontainer import OptionContainer
from toga.style import Pack

from .base import BaseSection
from .expenses import ExpensesSection
from flowat.const import style, icon

class MainSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
        self.add_expense_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_OUT,
                    id="expenses_button",
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Gastos", style=Pack(text_align="center", width=120)),
            ]
        )
        self.add_expense_button.enabled = False
        self.add_revenue_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_IN,
                    id="revenue_button",
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Receitas", style=Pack(text_align="center", width=120)),
            ]
        )
        self.report_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.BAR_CHART,
                    id="reports_button",
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Relatórios", style=Pack(text_align="center", width=120)),
            ]
        )
        self.preferences_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.SETTINGS,
                    id="preferences_button",
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Preferências", style=Pack(text_align="center", width=120)),
            ]
        )

        self.expense_section = ExpensesSection(app=self._app)

        self.buttons_container = Row(
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                self.report_button,
                self.preferences_button,
            ],
        )
        self.context_container = self.expense_section.full_contents
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="column"),
            children=[self.buttons_container, self.context_container],
        )

    def set_context_content(self, widget:Button):
        print(f"Changing context to: {widget.id}")
