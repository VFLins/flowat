from toga.widgets.imageview import ImageView
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.webview import WebView
from toga.widgets.divider import Divider
from toga.widgets.button import Button
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Row, Column
from toga.style import Pack

from datetime import date

from .base import BaseSection

from flowat.const import style, icon
from flowat.plot.bar import colplot
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
        self.plot_expense = WebView(
            style=Pack(width=style.CONTENT_WIDTH, height=220),
            content=colplot(
                x=["Dez. 2025", "Jan. 2026", "Fev. 2026", "Mar. 2026", "Abr. 2026"],
                y=[24133, 23122, 12011, 954, 97],
            ),
            on_webview_load=self.reload_plot,
        )

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
                Button(
                    id="btn_first_expense",
                    text="Inserir primerio gasto",
                    style=style.BIG_BUTTON,
                    on_press=self.show_form,
                ),
                Button(
                    id="btn_first_restore_backup",
                    text="Restaurar um backup",
                    style=style.BIG_BUTTON,
                ),
            ],
        )
        self.expense_form = Column(
            style=style.MAIN_CONTAINER,
            children=[
                Row(
                    style=Pack(align_items="center"),
                    children=[
                        FormField(
                            id="expense_form_type_selection",
                            input_widget=Selection(items=expense_categories),
                            label="Categoria",
                            unstyled=True,
                        ),
                        Button(
                            id="expense_form_edit_type",
                            icon=icon.CIRCLE_PLUS,
                            on_press=self.show_expense_type_dialog,
                        ),
                    ],
                ),
                FormField(
                    id="expense_form_description_search",
                    input_widget=TextInput(),
                    label="Descrição",
                    unstyled=True,
                ),
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
                        Button(
                            "Voltar",
                            style=style.SIMPLE_BUTTON,
                            on_press=self.show_main_content,
                        ),
                        Button(
                            "Inserir",
                            style=style.SIMPLE_BUTTON,
                            on_press=self.add_expense,
                        ),
                    ],
                ),
            ],
        )

        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER, children=[self.first_interaction]
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="column"),
            children=[self.main_container],
        )

    def reload_plot(self, widget: WebView):
        n_loads = getattr(widget, "_n_loads", 0)
        widget._n_loads = n_loads + 1
        if widget._n_loads % 2 == 1:
            return
        widget.content = colplot(
            x=["Dez. 2025", "Jan. 2026", "Fev. 2026", "Mar. 2026", "Abr. 2026"],
            y=[24133, 23122, 12011, 954, 297],
        )

    def add_expense(self, widget: Button):
        """Prompts to user to confirm the inserted data, in the positive case, writes
        to the database. Does nothing otherwise.
        """
        self.show_main_content(widget=widget)

    def show_form(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new expense.
        """
        self.main_container.clear()
        self.main_container.style = style.MAIN_CONTAINER
        self.main_container.add(self.expense_form)

    def show_main_content(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new expense.
        """
        self.main_container.clear()
        self.main_container.style = style.CENTERED_MAIN_CONTAINER
        new_container = self._get_main_container()
        self.main_container.add(new_container)

    def show_expense_type_dialog(self, widget: Button):
        """Show a dialog where the user can manage expense type options."""

    def _get_main_container(self):
        """Returns the 'common interaction' container, or 'first interaction' when
        there is no expense data in the database. The 'first interaction' container
        may include a 'restore backup' button if there's also no revenue data.
        """
        return self.first_interaction

    def _refresh_layout(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()
