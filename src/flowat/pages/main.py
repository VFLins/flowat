from toga.widgets.label import Label
from toga.widgets.button import Button
from toga.widgets.box import Box, Column, Row
from toga.style import Pack

from .base import BaseSection
from .expenses import ExpensesSection
from .revenues import RevenuesSection
from .report import ReportSection
from flowat.const import style, icon


class MainSection(BaseSection):
    EXPENSES_BUTTON = "expenses_button"
    REVENUES_BUTTON = "revenues_button"
    REPORTS_BUTTON = "reports_button"
    PREFERENCES_BUTTON = "preferences_button"

    def __init__(self, app):
        super().__init__(app=app)
        self.add_expense_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_OUT,
                    id=self.EXPENSES_BUTTON,
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                    enabled=False,
                ),
                Label("Gastos", style=Pack(text_align="center", width=120)),
            ],
        )
        self.add_revenue_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.MONEY_IN,
                    id=self.REVENUES_BUTTON,
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Receitas", style=Pack(text_align="center", width=120)),
            ],
        )
        self.report_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.BAR_CHART,
                    id=self.REPORTS_BUTTON,
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Relatórios", style=Pack(text_align="center", width=120)),
            ],
        )
        self.preferences_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(
                    icon=icon.SETTINGS,
                    id=self.PREFERENCES_BUTTON,
                    style=style.BIG_SQUARE_BUTTON,
                    on_press=self.set_context_content,
                ),
                Label("Preferências", style=Pack(text_align="center", width=120)),
            ],
        )

        self.expense_section = ExpensesSection(app=self._app)
        self.revenue_section = RevenuesSection(app=self._app)
        self.report_section = ReportSection(app=self._app)

        self.buttons_container = Row(
            style=Pack(margin=30),
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                self.report_button,
                self.preferences_button,
            ],
        )
        self.context_container = Box(
            style=Pack(direction="column", align_items="center", flex=1),
            children=[self.expense_section.full_contents],
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="column"),
            children=[self.buttons_container, self.context_container],
        )

    def set_context_content(self, widget: Button):
        buttons = (
            self.EXPENSES_BUTTON,
            self.REVENUES_BUTTON,
            self.REPORTS_BUTTON,
            self.PREFERENCES_BUTTON,
        )
        # INFO: enable other buttons, disable clicked
        for btn_id in buttons:
            self._app.widgets[btn_id].enabled = btn_id != widget.id
        self.context_container.clear()
        match widget.id:
            case self.REPORTS_BUTTON:
                clicked_section = self.report_section
            case self.REVENUES_BUTTON:
                clicked_section = self.revenue_section
            case self.EXPENSES_BUTTON:
                clicked_section = self.expense_section
            case _:
                clicked_section = BaseSection(app=self._app)
        self.context_container.add(clicked_section.full_contents)
        clicked_section.show_main_content()
        self.full_contents.refresh()
