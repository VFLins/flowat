from toga.widgets.label import Label
from toga.widgets.button import Button
from toga.widgets.box import Box, Column, Row
from toga.style import Pack

from .base import BaseSection
from .expenses import ExpensesSection
from .revenues import RevenuesSection
from flowat.const import style, icon


class MainSection(BaseSection):

    _BUTTON_IDS = [
        "expenses_button",
        "revenues_button",
        "reports_button",
        "preferences_button"
    ]

    def __init__(self, app):
        super().__init__(app=app)
        self.add_expense_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_OUT,
                    id=self._BUTTON_IDS[0],
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                    enabled=False,
                ),
                Label("Gastos", style=Pack(text_align="center", width=120)),
            ]
        )
        self.add_revenue_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_IN,
                    id=self._BUTTON_IDS[1],
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
                    id=self._BUTTON_IDS[2],
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Relatórios", style=Pack(
                    text_align="center", width=120)),
            ]
        )
        self.preferences_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.SETTINGS,
                    id=self._BUTTON_IDS[3],
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Preferências", style=Pack(
                    text_align="center", width=120)),
            ]
        )

        self.expense_section = ExpensesSection(app=self._app)
        self.revenue_section = RevenuesSection(app=self._app)

        self.buttons_container = Row(
            style=Pack(margin=30),
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

    def set_context_content(self, widget: Button):
        other_buttons = [
            self._app.widgets[id]
            for id in self._BUTTON_IDS
            if id != widget.id
        ]
        sections_contents = [
            self.expense_section.full_contents,
            self.revenue_section.full_contents,
        ]
        for btn in other_buttons:
            btn.enabled = True  # enable other buttons
        widget.enabled = False  # disable clicked button
        # remove previous section content
        self.full_contents.remove(*sections_contents)
        # add current section content
        if widget.id == self._BUTTON_IDS[1]:
            self.revenue_section._refresh_layout()
            self.full_contents.add(self.revenue_section.full_contents)
        if widget.id == self._BUTTON_IDS[0]:
            self.expense_section._refresh_layout()
            self.full_contents.add(self.expense_section.full_contents)
        self.full_contents.refresh()
