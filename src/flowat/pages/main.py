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
        self.add_expense_button = Button(
            "Inserir uma despesa", style=style.BIG_BUTTON,
        )
        self.add_revenue_button = Button(
            "Inserir uma receita", style=style.BIG_BUTTON,
        )
        self.fetch_revenue_button = Button(
            "Procurar transações", style=style.BIG_BUTTON,
        )

        self.buttons_container = Column(
            style=Pack(align_items="center", flex=1),
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                Divider(width=180, margin=10),
                self.fetch_revenue_button,
            ],
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1),
            children=[self.buttons_container],
        )
