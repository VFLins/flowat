from toga.widgets.table import Table
from toga.widgets.imageview import ImageView
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.divider import Divider
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Box, Row, Column
from toga.style import Pack

from datetime import date

from .base import BaseSection

from flowat.const import style
from flowat.form.date import HorizontalDateForm
from flowat.form.elem import FormField, Heading


class ExpensesSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
        expense_categories = [
            "Boleto bancário",
            "Cheque",
            "Folha de pagamento",
            "Tributo",
            "Conta (água, telefone, etc.)",
            "Fatura do cartão de crédito",
        ]
        expense_descriptions = [
            ("Fornecedor Recorrente Flautinha"),
            ("Conta de água: Filial 1"),
            ("Funcionários do atendimento"),
        ]

        # self.image_expense = ImageView(icon.MONEY_OUT_IMG)

        self.date_input = HorizontalDateForm(
            id="expense_form_duedate", value=date.today()
        )
        self.first_interaction = Column(
            children=[
                Button(
                    id="btn_first_expense",
                    text="Inserir primerio gasto",
                    style=style.BIG_BUTTON,
                ),
                Button(
                    id="btn_first_restore_backup",
                    text="Restaurar dados",
                    style=style.BIG_BUTTON,
                ),
            ]
        )
        self.expense_form = Column(
            style=style.MAIN_CONTAINER,
            children=[
                Heading("Informações", level=1),
                FormField(
                    id="expense_form_type_selection",
                    input_widget=Selection(items=expense_categories),
                    label="Categoria",
                    unstyled=True,
                ),
                FormField(
                    id="expense_form_description_search",
                    input_widget=TextInput(),
                    label="Descrição",
                    unstyled=True,
                ),
                Table(
                    id="expense_form_description_result",
                    data=expense_descriptions,
                    accessors=["name"],
                ),
                Heading("Valores", level=1),
                FormField(
                    id="expense_form_barcode",
                    input_widget=TextInput(),
                    label="Código de barras",
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
                        FormField(
                            id="expense_form_insert",
                            input_widget=Button("Inserir"),
                            label="",
                        ),
                    ],
                ),
            ],
        )

        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER, children=[self.expense_form]
        )
        self.full_contents = Box(
            style=Pack(align_items="start", flex=1, direction="column"),
            children=[
                # self.image_expense,
                self.main_container
            ],
        )

    def _refresh_layout(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()
