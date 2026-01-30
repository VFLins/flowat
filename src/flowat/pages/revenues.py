from toga.widgets.imageview import ImageView
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.webview import WebView
from toga.widgets.button import Button
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Column, Row
from toga.style import Pack

from datetime import date

from .base import BaseSection

from flowat.data import db, source
from flowat.const import icon, style
from flowat.form.elem import FormField
from flowat.form.date import HorizontalDateForm


class RevenuesSection(BaseSection):
    SELECTED_REVENUE = db.RevenueEntry()
    revenues_source = source.RevenuesSource()
    agg_revenues_source = source.AggregatedRevenuesSource()

    def __init__(self, app):
        super().__init__(app=app)

        revenue_types = [
            "Recebível à vista",
            "Parcela de recebível à prazo",
        ]
        self.plot_revenue = WebView(
            style=Pack(width=515, height=160),
            on_webview_load=self._on_reload_plot,
        )
        self.date_input = HorizontalDateForm(
            id="expense_form_duedate", value=date.today()
        )
        self.revenues_list = Table(
            style=Pack(flex=1),
            on_select=self._on_select_revenue,
            headings=["Descrição", "Tipo", "Valor", "Data"]
        )
        self.revenues_list_annotation = Label(
            style=Pack(font_size=9, margin=5, flex=1), text=""
        )
        self.revenue_details_button = Button(
            text="ⓘ",
            enabled=False,
            style=style.SIMPLE_SQUARE_BUTTON,
            on_press=self.show_expense_details_dialog,
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
        self.revenue_summary = Column(
            style=style.MAIN_CONTAINER,
            children=[
                self.plot_revenue,
                Row(style=Pack(align_items="center"), children=[
                    TextInput(
                        id="revenue_summary_search",
                        placeholder="Pesquisa",
                        style=Pack(margin=5, flex=1),
                        on_change=self._on_search_update,
                    ),
                    Button("Adic. ↓", style=style.SIMPLE_BUTTON, on_press=self.change_sorting),
                    Button(
                        text="🗑",
                        style=style.SIMPLE_SQUARE_BUTTON,
                        on_press=self.rm_expense,
                    ),
                    self.expense_details_button,
                    Button(
                        text="+",
                        style=style.SIMPLE_SQUARE_BUTTON,
                        on_press=self.show_form,
                    ),
                ]),
                self.expenses_list,
                Row(style=Pack(align_items="center"), children=[
                    self.revenues_list_annotation,
                    Button("anterior", style=style.SIMPLE_SMALL_BUTTON),
                    Button("próximo", style=style.SIMPLE_SMALL_BUTTON),
                ])
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

    def show_main_content(self, widget: Button):
        """Removes currently displayed elments and show a summary of revenues."""
        self.main_container.clear()
        if db.ExpenseEntry().table_is_empty():
            self.main_container.style = style.CENTERED_MAIN_CONTAINER
        else:
            self.main_container.style = style.MAIN_CONTAINER
        new_container = self._get_main_container()
        self.main_container.add(new_container)

    def _on_reload_plot(self, widget: WebView):
        n_loads = getattr(widget, "_n_loads", 0)
        widget._n_loads = n_loads + 1
        if widget._n_loads % 2 == 1:
            return
        dates, sums = zip(*self.agg_revenues_source.current_data)
        print(f"INFO: Loading plot data {dates=}, {sums=}")
        widget.content = colplot(x=dates, y=sums)

    def _on_select_revenue(self, widget: Table):
        """Actions performed when an expense is selected or `widget` loses selection."""
        if widget.selection is None:
            self.revenue_details_button.enabled = False
            self.SELECTED_REVENUE.clear()
        else:
            self.revenue_details_button.enabled = True
            self.SELECTED_REVENUE.read(row_id=widget.selection.id)
            print(f"INFO: selected expense id: {self.SELECTED_REVENUE.Id}")

    def _on_search_update(self, widget: TextInput):
        """Actions performed when the user interacts with the search bar in the expese
        summary.
        """
        search_widget = self._app.widgets["revenue_summary_search"]
        self.revenues_source.search_text = search_widget.value
        self._refresh_displayed_data()

    def _refresh_displayed_data(self):
        """Refreshes data displayed in the summary section from both plot and table."""
        self.revenues_list.data = None # winforms needs to clear before filling
        self.revenues_list.data=[
            {
                "tipo": r.TransactionType,
                "descrição": r.Description,
                "valor": r.TransactionValue,
                "vencimento": r.TransactionDate,
                "id": r.Id,
            }
            for r in self.revenues_source.current_data
        ]
        self.revenues_list_annotation.text = (
            f"{self.revenues_source.nrows} itens, "
            f"mostrando {self.revenues_source.min_idx + 1} "
            f"até {self.revenues_source.max_idx}"
        )
        dates, sums = zip(*self.agg_revenues_source.current_data)
        print(f"INFO: Loading plot data: {dates=}, {sums=}")
        self.plot_revenue.content = colplot(x=dates, y=sums)

    def _build_layout0(self) -> Box:
        no_expense_data = True
        no_data = True
        container = Box()
