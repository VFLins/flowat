from toga.widgets.label import Label
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.box import Box, Column, Row
from toga.widgets.optioncontainer import OptionContainer
from toga.style import Pack

from .base import BaseSection
from flowat.const import style, icon

class MainSection(BaseSection):
    def __init__(self):
        super().__init__()
        self.add_expense_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(icon=icon.MONEY_OUT, style=style.BIG_SQUARE_BUTTON),
                Label("Inserir um gasto", style=Pack(text_align="center", font_size=10, width=120)),
            ]
        )
        self.add_revenue_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(icon=icon.MONEY_IN, style=style.BIG_SQUARE_BUTTON),
                Label("Inserir uma receita", style=Pack(text_align="center", font_size=10, width=160)),
            ]
        )
        self.fetch_revenue_button = Column(
            style=Pack(align_items="center"),
            children=[
                Button(icon=icon.SETTINGS, style=style.BIG_SQUARE_BUTTON),
                Label("Preferências", style=Pack(text_align="center", font_size=10, width=120)),
            ]
        )

        self.buttons_container = Row(
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                self.fetch_revenue_button,
            ],
        )
        self.full_contents = Box(
            style=Pack(align_items="start", flex=1, direction="column"),
            children=[self.buttons_container],
        )
