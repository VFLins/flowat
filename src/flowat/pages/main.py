from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.box import Box, Column
from toga.widgets.optioncontainer import OptionContainer
from toga.style import Pack

from .base import BaseSection
from flowat.const import style, icon

class MainSection(BaseSection):
    def __init__(self):
        super().__init__()
        self.add_expense_button = Button(icon=icon.CIRCLE_MINUS, style=style.BIG_BUTTON)
        self.add_revenue_button = Button(icon=icon.CIRCLE_PLUS, style=style.BIG_BUTTON)
        self.fetch_revenue_button = Button(icon=icon.SCAN_SEARCH, style=style.BIG_BUTTON)

        self.buttons_container = Column(
            style=Pack(align_items="center", flex=1),
            children=[
                self.add_expense_button,
                self.add_revenue_button,
                self.fetch_revenue_button,
            ],
        )
        self.main_container = Box(
            style=Pack(align_items="center", flex=1),
            children=[self.buttons_container],
        )
        self.full_contents = OptionContainer(
            style=Pack(align_items="center"),
            content=[("Home", self.main_container)]
        )
