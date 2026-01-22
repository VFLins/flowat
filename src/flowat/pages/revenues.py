from toga.widgets.imageview import ImageView
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Box, Column, Row
from toga.style import Pack

from datetime import date

from .base import BaseSection

from flowat.const import icon, style
from flowat.form.elem import FormField
from flowat.form.date import HorizontalDateForm


class RevenuesSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)

        revenue_types = [
            "Recebível à vista",
            "Parcela de recebível à prazo",
        ]
        self.date_input = HorizontalDateForm(
            id="expense_form_duedate", value=date.today()
        )

        self.first_interaction = Column(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[
                ImageView(
                    image=icon.MISSING_ITEM_IMG,
                    style=Pack(margin=20, width=96, height=96),
                ),
                Label(
                    "Nenhum registro encontrado, você pode:",
                    style=Pack(font_size=13, text_align="center", margin=(0, 0, 30, 0)),
                ),
                Button("Inserir primeira receita", style=style.BIG_BUTTON, on_press=self.show_form),
                Button("Ler vendas do PDV", style=style.BIG_BUTTON),
                Button("Restaurar um backup", style=style.BIG_BUTTON)
            ],
        )
        self.revenue_form = Column(
            style=style.MAIN_CONTAINER,
            children=[
                FormField(
                    id="revenue_form_type",
                    input_widget=Selection(items=revenue_types),
                    label="Tipo",
                    unstyled=True,
                ),
                FormField(
                    id="revenue_form_description",
                    input_widget=TextInput(),
                    label="Descrição",
                    unstyled=True,
                ),
                self.date_input.widget,
                Row(
                    style=Pack(align_items="end"),
                    children=[
                        FormField(
                            id="expense_form_value",
                            input_widget=TextInput(placeholder="0,00"),
                            label="Valor",
                        ),
                        Button(
                            "Voltar",
                            style=style.SIMPLE_BUTTON,
                        ),
                        Button(
                            "Inserir",
                            style=style.SIMPLE_BUTTON,
                        ),
                    ],
                ),
            ]
        )
        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[self.first_interaction],
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="row"),
            children=[
                # self.image_expense,
                self.main_container
            ],
        )


    def show_form(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new revenue.
        """
        self.main_container.clear()
        self.main_container.style = style.MAIN_CONTAINER
        self.main_container.add(self.revenue_form)

    def _build_layout0(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()
