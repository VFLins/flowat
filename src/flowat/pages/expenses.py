from toga.widgets.imageview import ImageView
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Box
from toga.style import Pack

from .base import BaseSection

from flowat.const import icon, style


class ExpensesSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)

        #self.image_expense = ImageView(icon.MONEY_OUT_IMG)
        self.add_first_expense = Button("Adicionar primerio gasto", style=style.BIG_BUTTON)
        self.restore_data = Button("Restaurar seu banco de dados", style=style.BIG_BUTTON)

        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="column"),
            children=[
                #self.image_expense,
                self.add_first_expense,
                Label("ou", style=style.BIG_BUTTON),
                self.restore_data,
            ]
        )
