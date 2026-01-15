from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.box import Box, Column
from toga.style import Pack

from .base import BaseSection


class MainSection(BaseSection):
    def __init__(self):
        super().__init__()
        self.add_expense_button = Button(
            "Adicionar despesa",
            style=Pack(width=200),
        )
        self.add_revenue_button = Button(
            "Adicionar receita",
            style=Pack(width=200),
        )
        self.fetch_revenue_button = Button(
            "Procurar receitas",
            style=Pack(width=200),
        )

        self.buttons_container = Column(
            style=Pack(align_items="center", flex=1),
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                self.fetch_revenue_button,
            ],
        )

        self.full_contents = Box(
            style=Pack(align_items="center", flex=1),
            children=[self.buttons_container]
        )
