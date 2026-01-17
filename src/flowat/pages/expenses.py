from toga.widgets.detailedlist import DetailedList
from toga.widgets.imageview import ImageView
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Box, Row, Column
from toga.style import Pack

from datetime import date

from .base import BaseSection

from flowat.const import icon, style
from flowat.form.date import VerticalDateForm
from flowat.form.elem import FormField


class ExpensesSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
        expense_categories = [
            "Boleto bancário",
            "Cheque",
            "Folha de pagamento",
            "Tributo",
            "Conta (água, telefone, etc.)",
            "Fatura do cartão de crédito"
        ]

        #self.image_expense = ImageView(icon.MONEY_OUT_IMG)

        self.date_input = VerticalDateForm(
            id="expense_form_duedate",
            value=date.today()
        )
        self.first_interaction = Column(children=[
            Button(
                id="btn_first_expense",
                text="Inserir primerio gasto",
                style=style.BIG_BUTTON
            ),
            Button(
                id="btn_first_restore_backup",
                text="Restaurar dados",
                style=style.BIG_BUTTON
            ),
        ])
        self.expense_form = Row(children=[
            Column(children=[
                TextInput(id="expense_form_description_search", placeholder="Descrição"),
                DetailedList(id="expense_form_description_result"),
                Label("Categoria"),
                Selection(id="expense_form_type_selection", items=expense_categories),
            ]),
            Column(children=[
                self.date_input.widget,
                FormField(
                    id="expense_form_value",
                    input_widget=TextInput,
                    label="valor",
                )
            ])
        ])

        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[self.expense_form]
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="row"),
            children=[
                #self.image_expense,
                self.main_container
            ]
        )

    def _refresh_layout(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()

