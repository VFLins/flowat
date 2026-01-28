from toga.widgets.imageview import ImageView
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.webview import WebView
from toga.widgets.divider import Divider
from toga.widgets.button import Button
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Row, Column
from toga.dialogs import InfoDialog
from toga.window import Window
from toga.style import Pack

from datetime import date, datetime
import asyncio

from .base import BaseSection

from flowat.const import style, icon
from flowat.data import db, source, fmt
from flowat.plot.bar import colplot
from flowat.form.date import HorizontalDateForm
from flowat.form.elem import FormField, Heading


class ExpensesSection(BaseSection):
    SELECTED_EXPENSE = db.ExpenseEntry()
    expenses_source = source.ExpensesSource()
    expense_type_source = source.ExpenseTypeSource()

    def __init__(self, app):
        super().__init__(app=app)
        self._ensure_expense_types()
        self.plot_expense = WebView(
            style=Pack(width=style.CONTENT_WIDTH, height=160),
            content=colplot(
                x=["Dez. 2025", "Jan. 2026", "Fev. 2026", "Mar. 2026", "Abr. 2026"],
                y=[24133, 23122, 12011, 954, 97],
            ),
            on_webview_load=self.reload_plot,
        )
        self.date_input = HorizontalDateForm(
            id="expense_form_duedate", value=date.today()
        )
        self.expenses_list = Table(
            style=Pack(flex=1),
            on_select=self._on_select_expense,
            headings=["Descrição", "Valor", "Vencimento"],
        )
        self.expenses_list_annotation = Label(
            style=Pack(font_size=9, margin=5, flex=1), text=""
        )
        self.expenses_source.sort_ascending = False
        self._refresh_displayed_data()

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
        self.expense_summary = Column(
            style=style.MAIN_CONTAINER,
            children=[
                self.plot_expense,
                Row(style=Pack(align_items="center"), children=[
                    TextInput(placeholder="Pesquisa", style=Pack(margin=5, flex=1)),
                    Button("Adic. ↓", style=style.SIMPLE_BUTTON, on_press=self.change_sorting),
                    Button(
                        text="⋮",
                        id="selected_expense_details_button",
                        enabled=False,
                        style=style.SIMPLE_SQUARE_BUTTON,
                        on_press=self.show_expense_details_dialog,
                    ),
                    Button(
                        text="+",
                        style=style.SIMPLE_SQUARE_BUTTON,
                        on_press=self.show_form
                    ),
                ]),
                self.expenses_list,
                Row(style=Pack(align_items="center"), children=[
                    self.expenses_list_annotation,
                    Button("anterior", style=Pack(height=28, font_size=9, margin=5)),
                    Button("próximo", style=Pack(height=28, font_size=9, margin=5)),
                ])
            ]
        )
        self.expense_form = Column(
            style=style.MAIN_CONTAINER,
            children=[
                FormField(
                    id="expense_form_type_selection",
                    input_widget=Selection(
                        items=[r.Name for r in self.expense_type_source.current_data],
                    ),
                    label="Categoria",
                    unstyled=True,
                ),
                FormField(
                    id="expense_form_description_search",
                    input_widget=TextInput(on_change=self._on_form_update),
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
                            input_widget=TextInput(
                                placeholder="0,00", on_change=self._on_form_update
                            ),
                            label="Valor",
                        ),
                        Button(
                            "Voltar",
                            style=style.SIMPLE_BUTTON,
                            on_press=self.show_main_content,
                        ),
                        Button(
                            "Inserir",
                            id="expense_form_confirm",
                            style=style.SIMPLE_BUTTON,
                            enabled=False,
                            on_press=self.add_expense,
                        ),
                    ],
                ),
            ],
        )

        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER, children=[self._get_main_container()]
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
        expense = self._get_expense_form_entry()
        # TODO: add confirmation dialog
        expense.write()
        self._refresh_displayed_data()
        self.show_main_content(widget=widget)

    def show_form(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new expense.
        """
        self.main_container.clear()
        self.main_container.style = style.MAIN_CONTAINER
        self.main_container.add(self.expense_form)

    def _on_select_expense(self, widget: Table):
        """Actions performed when an expense is selected or `widget` loses selection."""
        if widget.selection is None:
            self._app.widgets["selected_expense_details_button"].enabled = False
            self.SELECTED_EXPENSE.clear()
        else:
            self._app.widgets["selected_expense_details_button"].enabled = True
            self.SELECTED_EXPENSE.read(row_id=widget.selection.id)
            print(f"INFO: selected expense id: {self.SELECTED_EXPENSE.Id}")

    def _get_expense_form_entry(self) -> db.ExpenseEntry:
        type_field: Selection = self._app.widgets["expense_form_type_selection"]
        type_map = {name: id for id, name in self.expense_type_source.current_data}
        barcode_fmt = fmt.StringToBarcodeITF25(
            user_input=self._app.widgets["expense_form_barcode"].input.value,
            field_name="Código de Barra",
        )
        value_fmt = fmt.StringToCurrency(
            user_input=self._app.widgets["expense_form_value"].input.value,
            field_name="Valor",
        )
        return db.ExpenseEntry(
            IdExpenseType=type_map[type_field.input.value],
            TimeStamp=datetime.now(),
            Description=self._app.widgets["expense_form_description_search"].input.value,
            Barcode=barcode_fmt.value,
            TransactionDate=self.date_input.value,
            TransactionValue=value_fmt.value,
        )

    def _on_form_update(self, widget: TextInput):
        """Actions performed when the user interacts with any input in the expense
        form.
        """
        expense = self._get_expense_form_entry()
        if expense.required_fields_are_filled():
            self._app.widgets["expense_form_confirm"].enabled = True
        else:
            self._app.widgets["expense_form_confirm"].enabled = False

    def _refresh_displayed_data(self):
        """Refreshes data displayed in the summary section from both plot and table."""
        self.expenses_list.data=[
            {
                "descrição": r.Description,
                "valor": f"{r.TransactionValue}".replace(".", ","),
                "vencimento": r.TransactionDate,
                "id": r.Id,
            }
            for r in self.expenses_source.current_data
        ]
        self.expenses_list_annotation.text = (
            f"{self.expenses_source.nrows} itens, "
            f"mostrando {self.expenses_source.min_idx + 1} "
            f"até {self.expenses_source.max_idx}"
        )

    def show_main_content(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new expense.
        """
        self.main_container.clear()
        expense_data = db.ExpenseEntry()
        if expense_data.table_is_empty():
            self.main_container.style = style.CENTERED_MAIN_CONTAINER
        else:
            self.main_container.style = style.MAIN_CONTAINER
        new_container = self._get_main_container()
        self.main_container.add(new_container)

    def change_sorting(self, widget: Button):
        sort_options = ["Adic. ↓", "Adic. ↑", "Venc. ↓", "Venc. ↑"]
        current_idx = sort_options.index(widget.text)
        widget.text = sort_options[0 if current_idx==len(sort_options) - 1 else current_idx + 1]
        match widget.text:
            case "Venc. ↑":
                self.expenses_source.sort_column = "TransactionDate"
                self.expenses_source.sort_ascending = True
            case "Venc. ↓":
                self.expenses_source.sort_column = "TransactionDate"
                self.expenses_source.sort_ascending = False
            case "Adic. ↑":
                self.expenses_source.sort_column = "Id"
                self.expenses_source.sort_ascending = True
            case _:
                self.expenses_source.sort_column = "Id"
                self.expenses_source.sort_ascending = False
        self._refresh_displayed_data()

    def show_expense_details_dialog(self, widget: Button):
        """Show a dialog with details of the selected expense."""
        info_dialog = InfoDialog("Informações do gasto", str(self.SELECTED_EXPENSE))
        asyncio.create_task(self._app.main_window.dialog(info_dialog))

    def show_expense_type_dialog(self, widget: Button):
        """Show a dialog where the user can manage expense type options."""

    def _get_main_container(self):
        """Returns the 'common interaction' container, or 'first interaction' when
        there is no expense data in the database. The 'first interaction' container
        may include a 'restore backup' button if there's also no revenue data.
        """
        expense_data = db.ExpenseEntry()
        if expense_data.table_is_empty():
            return self.first_interaction
        else:
            return self.expense_summary

    def _refresh_layout(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()

    def _ensure_expense_types(self):
        expense_categories = [
            "Boleto Bancário",
            "Cheque",
            "Folha de Pagamento",
            "Tributo",
            "Conta (Água, Telefone, Etc.)",
            "Fatura Do Cartão De Crédito",
        ]
        current_data = [r.Name for r in self.expense_type_source.current_data]
        for categ in expense_categories:
            if categ not in current_data:
                et = db.ExpenseType(Name=categ)
                et.write()
