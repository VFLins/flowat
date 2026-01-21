from toga.widgets.imageview import ImageView
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Box
from toga.style import Pack

from .base import BaseSection

from flowat.const import icon, style


class RevenuesSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)

        # self.image_revenue = ImageView(icon.MONEY_OUT_IMG)
        self.add_first_revenue_button = Button(
            "Inserir primeira receita", style=style.BIG_BUTTON
        )
        self.restore_data_button = Button("Restaurar dados", style=style.BIG_BUTTON)

        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[
                ImageView(image=icon.MISSING_ITEM_IMG, style=Pack(margin=30)),
                Label("Nenhum registro encontrado, você pode:", style=Pack(font_size=16, text_align="center", margin=(0, 0, 60, 0))),
                self.add_first_revenue_button,
                Label("ou", style=Pack(text_align="center")),
                self.restore_data_button,
                Label("ou", style=Pack(text_align="center")),
                Button("Ler vendas do PDV", style=style.BIG_BUTTON),
            ],
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="row"),
            children=[
                # self.image_expense,
                self.main_container
            ],
        )

    def _build_layout0(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()
