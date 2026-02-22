from toga.widgets.activityindicator import ActivityIndicator
from toga.widgets.imageview import ImageView
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.webview import WebView
from toga.widgets.button import Button
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Column, Row
from toga.widgets.optioncontainer import OptionContainer
from toga.widgets.scrollcontainer import ScrollContainer
from toga.dialogs import InfoDialog, ConfirmDialog, SelectFolderDialog
from toga.style import Pack

from datetime import date, datetime
import asyncio
import nflogic

from .base import BaseSection

from flowat.data import db, source, fmt, nf
from flowat.const import icon, style
from flowat.plot.bar import colplot
from flowat.form.elem import FormField
from flowat.form.date import HorizontalDateForm


class RevenuesSection(BaseSection):
    SELECTED_REVENUE = db.RevenueEntry()
    revenues_source = source.RevenuesSource()
    agg_revenues_source = source.AggregatedRevenuesSource()
    revenue_type_source = source.RevenueTypeSource()

    def __init__(self, app):
        super().__init__(app=app)
        self._ensure_revenue_types()
        self.plot_revenue = WebView(
            style=Pack(width=515, height=160),
            on_webview_load=self._on_reload_plot,
        )
        self.date_input = HorizontalDateForm(value=date.today())
        self.revenues_list = Table(
            style=Pack(flex=1),
            on_select=self._on_select_revenue,
            headings=["Descrição", "Tipo", "Valor", "Data"],
        )
        self.revenues_list_annotation = Label(
            style=Pack(font_size=9, margin=5, flex=1), text=""
        )
        self.revenue_details_button = Button(
            text="ⓘ",
            enabled=False,
            style=style.SIMPLE_SQUARE_BUTTON,
            on_press=self.show_revenue_details_dialog,
        )
        self.delete_revenue_button = Button(
            text="🗑",
            style=style.SIMPLE_SQUARE_BUTTON,
            on_press=self.rm_revenue,
        )
        self.scan_activity = ActivityIndicator()
        self.scan_info = Label(text="", style=Pack(font_size=13))
        self.scan_docs_button = FormField(
            label="Ações",
            input_widget=Button(
                text="Escanear uma pasta",
                style=style.user_input(Button),
                on_press=self.nflogic_scan,
            ),
            description="Escaneia dados dos arquivos\nde uma pasta",
        )
        self.add_scanned_data_button = FormField(
            label="",
            input_widget=Button("Selecionar dados", on_press=self.add_scanned_revenues),
            description="Seleciona dados disponíveis\npara inserir",
        )
        self.revenues_source.sort_ascending = False

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
                    "Inserir primeira receita",
                    style=style.BIG_BUTTON,
                    on_press=self.show_form,
                ),
                Button("Ler vendas do PDV", style=style.BIG_BUTTON),
                Button("Restaurar um backup", style=style.BIG_BUTTON),
            ],
        )
        self.revenue_summary = Column(
            style=style.MAIN_CONTAINER,
            children=[
                self.plot_revenue,
                Row(
                    style=Pack(align_items="center"),
                    children=[
                        TextInput(
                            id="revenue_summary_search",
                            placeholder="Pesquisa",
                            style=Pack(margin=5, flex=1),
                            on_change=self._on_search_update,
                        ),
                        Button(
                            "Adic. ↓",
                            style=style.SIMPLE_BUTTON,
                            on_press=self.change_sorting,
                        ),
                        self.delete_revenue_button,
                        self.revenue_details_button,
                        Button(
                            text="+",
                            style=style.SIMPLE_SQUARE_BUTTON,
                            on_press=self.show_form,
                        ),
                    ],
                ),
                self.revenues_list,
                Row(
                    style=Pack(align_items="center"),
                    children=[
                        self.revenues_list_annotation,
                        Button("anterior", style=style.SIMPLE_SMALL_BUTTON),
                        Button("próximo", style=style.SIMPLE_SMALL_BUTTON),
                    ],
                ),
            ],
        )
        self.revenue_input_form = Column(
            style=style.MAIN_CONTAINER,
            children=[
                FormField(
                    id="revenue_form_type",
                    container_style=Pack(width=style.FORM_WIDTH),
                    input_widget=Selection(
                        on_change=self._on_form_update,
                        items=[r.Name for r in self.revenue_type_source.current_data],
                    ),
                    label="Tipo",
                    unstyled=True,
                ),
                FormField(
                    id="revenue_form_description",
                    container_style=Pack(width=style.FORM_WIDTH),
                    input_widget=TextInput(on_change=self._on_form_update),
                    label="Descrição",
                    unstyled=True,
                ),
                self.date_input.widget,
                Row(
                    style=Pack(align_items="end"),
                    children=[
                        FormField(
                            id="revenue_form_value",
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
                            id="revenue_form_confirm",
                            enabled=False,
                            style=style.SIMPLE_BUTTON,
                            on_press=self.add_revenue,
                        ),
                    ],
                ),
            ],
        )
        self.revenue_scan_form_step1 = Row(
            style=style.CENTERED_FORM_CONTAINER,
            children=[self.scan_docs_button, self.add_scanned_data_button],
        )
        self.revenue_scan_form_step2 = FormField(
            label="Vendedores encontrados",
            input_widget=Table(
                headings=["Razão social do vendedor"],
                on_activate=self.add_scanned_revenues,
            ),
            description="Escolha um item com um clique duplo.",
        )
        self.revenue_scan_form_step3 = Column()
        self.revenue_scan_form = ScrollContainer(
            content=Column(
                style=style.CENTERED_MAIN_CONTAINER,
                children=[
                    ImageView(
                        image=icon.SCANNER_IMG,
                        style=Pack(margin=(40, 0, 20, 0), width=96, height=96),
                    ),
                    Row(children=[self.scan_activity, self.scan_info]),
                    self.revenue_scan_form_step1,
                    Row(
                        style=style.FORM_CONTAINER,
                        children=[
                            Box(style=Pack(flex=1)),  # push buttons to the right side
                            Button(
                                "Voltar",
                                style=style.SIMPLE_BUTTON,
                                on_press=self.show_main_content,
                            ),
                            Button(
                                "Inserir",
                                style=style.RIGHTMOST_SIMPLE_BUTTON,
                                enabled=False,
                                on_press=self.add_scanned_revenues,
                            ),
                        ],
                    ),
                ],
            )
        )
        self.revenue_form = OptionContainer(
            style=style.MAIN_CONTAINER,
            content=[
                ("Inserção manual", self.revenue_input_form),
                ("Escanear notas de venda", self.revenue_scan_form),
            ],
        )
        self.main_container = Box(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[self.first_interaction],
        )
        self.full_contents = Box(
            style=Pack(align_items="center", flex=1, direction="row"),
            children=[self.main_container],
        )

    def show_form(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new revenue.
        """
        self.main_container.clear()
        self.main_container.add(self.revenue_form)
        asyncio.create_task(self._check_available_scanned_data())

    def show_main_content(self, widget: Button | None = None):
        """Removes currently displayed elments and show a summary of revenues."""
        self.main_container.clear()
        if db.RevenueEntry().table_is_empty():
            self.main_container.style = style.CENTERED_MAIN_CONTAINER
        else:
            self.main_container.style = style.MAIN_CONTAINER
        new_container = self._get_main_container()
        self.main_container.add(new_container)

    def show_revenue_details_dialog(self, widget: Button):
        """Show a dialog with details of the selected revenue."""
        info_dialog = InfoDialog(
            "Informações desta receita", str(self.SELECTED_REVENUE)
        )
        asyncio.create_task(self._app.main_window.dialog(info_dialog))

    def add_revenue(self, widget: Button):
        """Prompts to user to confirm the inserted data, in the positive case, writes
        to the database. Does nothing otherwise.
        """
        revenue = self._get_revenue_form_entry()
        # TODO: Add confirmation dialog. Should check if a similar transaction was
        # added before (type, value and date), and warn the user.
        revenue.write()
        self._clear_revenue_form()
        self._refresh_displayed_data()
        self.show_main_content(widget=widget)

    def rm_revenue(self, widget: Button):
        """Prompts the user to confirm removal of the selected revenue. Calls
        `self.rm_revenue_response` to handle the user's response.
        """
        confirm_dialog = ConfirmDialog(
            "Excluir esta receita?", str(self.SELECTED_REVENUE)
        )
        task = asyncio.create_task(self._app.main_window.dialog(confirm_dialog))
        task.add_done_callback(self.rm_revenue_response)

    def rm_revenue_response(self, task: asyncio.Task):
        """Handles user's response to the dialog invoked by `self.rm_revenue`."""
        if task.result():
            self.SELECTED_REVENUE.delete()
            self._refresh_displayed_data()
            self.show_main_content()

    def nflogic_scan(self, widget: Button):
        """Prompts the user to select a directory to be scanned for revenue documents.
        Calls `self.nflogic_scan_response` to handle the user's response.
        """
        dir_dialog = SelectFolderDialog(
            title="Selecione a pasta com os documentos fiscais (NFe)"
        )
        task = asyncio.create_task(self._app.main_window.dialog(dir_dialog))
        task.add_done_callback(self.nflogic_scan_response)

    def nflogic_scan_response(self, task: asyncio.Task):
        """Handles user's response to the dialog invoked by `self.nflogic_scan`."""
        result = task.result()
        print(f"INFO: User selected directory for scanning: {result}")
        if result:
            self._scan_documents(dir_path=result)

    async def _check_available_scanned_data(self):
        """Allows the user to add scanned data if any is available, forbids otherwise."""
        self.add_scanned_data_button.input.enabled = False
        self.scan_activity.start()
        self.scan_info.text = "Procurando dados para adicionar..."
        seller_names = nf.get_seller_names()
        self.AVAILABLE_SELLER_NAMES, acm_count = [], 0
        for seller in seller_names:
            count = await asyncio.to_thread(
                nf.count_new_seller_data, seller_name=seller
            )
            if count > 0:
                self.AVAILABLE_SELLER_NAMES.append(seller.display_name)
                acm_count = acm_count + count
        self.scan_activity.stop()
        if acm_count == 0:
            self.scan_info.text = "Nenhum dado disponível para inserir."
        else:
            self.scan_info.text = f"Dados de {acm_count} documentos encontrados."
            self.add_scanned_data_button.input.enabled = True

    def _scan_documents(self, dir_path: str):
        """Handles user interaction when adding data from processed documents."""
        self.scan_activity.start()
        self.scan_info.text = "Processando documentos, aguarde..."
        nflogic.parse_dir(dir_path=dir_path, buy=False, full_parse=False)
        self.scan_activity.stop()
        asyncio.create_task(self._check_available_scanned_data())

    def add_scanned_revenues(self, widget: Table):
        """Adds any data from the selected seller name to the database."""

    def change_sorting(self, widget: Button):
        sort_options = ["Adic. ↓", "Adic. ↑", "Venc. ↓", "Venc. ↑"]
        current_idx = sort_options.index(widget.text)
        widget.text = sort_options[
            0 if current_idx == len(sort_options) - 1 else current_idx + 1
        ]
        match widget.text:
            case "Venc. ↑":
                self.revenues_source.sort_column = "TransactionDate"
                self.revenues_source.sort_ascending = True
            case "Venc. ↓":
                self.revenues_source.sort_column = "TransactionDate"
                self.revenues_source.sort_ascending = False
            case "Adic. ↑":
                self.revenues_source.sort_column = "Id"
                self.revenues_source.sort_ascending = True
            case _:
                self.revenues_source.sort_column = "Id"
                self.revenues_source.sort_ascending = False
        self._refresh_displayed_data()

    def _on_reload_plot(self, widget: WebView, **kwargs):
        n_loads = getattr(widget, "_n_loads", 0)
        widget._n_loads = n_loads + 1
        if widget._n_loads % 2 == 1:
            return
        plot_data = self.agg_revenues_source.current_data
        if plot_data:
            dates, sums = zip(*plot_data[:6])  # first 6 months starting from current
            print(f"INFO: Loading plot data: {dates=}, {sums=}")
            self.plot_revenue.content = colplot(x=dates, y=sums)

    def _on_select_revenue(self, widget: Table):
        """Actions performed when an revenue is selected or `widget` loses selection."""
        if widget.selection is None:
            self.delete_revenue_button.enabled = False
            self.revenue_details_button.enabled = False
            self.SELECTED_REVENUE.clear()
        else:
            self.delete_revenue_button.enabled = True
            self.revenue_details_button.enabled = True
            self.SELECTED_REVENUE.read(row_id=widget.selection.id)
            print(f"INFO: selected revenue id: {self.SELECTED_REVENUE.Id}")

    def _on_search_update(self, widget: TextInput):
        """Actions performed when the user interacts with the search bar in the expese
        summary.
        """
        search_widget = self._app.widgets["revenue_summary_search"]
        self.revenues_source.search_text = search_widget.value
        self._refresh_displayed_data()

    def _refresh_displayed_data(self):
        """Refreshes data displayed in the summary section from both plot and table."""
        self.revenues_list.data = None  # winforms needs to clear before filling
        self.revenues_list.data = [
            {
                "tipo": r.TransactionType,
                "descrição": r.Description,
                "valor": r.TransactionValue,
                "data": r.TransactionDate,
                "id": r.Id,
            }
            for r in self.revenues_source.current_data
        ]
        self.revenues_list_annotation.text = (
            f"{self.revenues_source.nrows} itens, "
            f"mostrando {self.revenues_source.min_idx + 1} "
            f"até {self.revenues_source.max_idx}"
        )
        plot_data = self.agg_revenues_source.current_data
        if plot_data:
            dates, sums = zip(*plot_data[:6])  # first 6 months starting from current
            print(f"INFO: Loading plot data: {dates=}, {sums=}")
            self.plot_revenue.content = colplot(x=dates, y=sums)

    def _get_main_container(self):
        """Returns the 'common interaction' container, or 'first interaction' when
        there is no revenue data in the database. The 'first interaction' container
        may include a 'restore backup' button if there's also no revenue data.
        """
        if db.RevenueEntry().table_is_empty():
            return self.first_interaction
        else:
            return self.revenue_summary

    def _clear_revenue_form(self):
        """Resets revenue form fields to their default values."""
        # revenue type
        type_field = self._app.widgets["revenue_form_type"]
        type_data = self.revenue_type_source.current_data
        type_field.value = type_data[0].Name if bool(type_data) else ""
        # description
        self._app.widgets["revenue_form_description"].input.value = ""
        # date
        self.date_input.value = date.today()
        # value
        self._app.widgets["revenue_form_value"].input.value = ""

    def _get_revenue_form_entry(self) -> db.RevenueEntry:
        type_field: Selection = self._app.widgets["revenue_form_type"]
        type_map = {name: id for id, name in self.revenue_type_source.current_data}
        value_fmt = fmt.StringToCurrency(
            user_input=self._app.widgets["revenue_form_value"].input.value,
            field_name="Valor",
        )
        return db.RevenueEntry(
            IdRevenueType=type_map[type_field.input.value],
            TimeStamp=datetime.now(),
            Description=self._app.widgets["revenue_form_description"].input.value,
            TransactionDate=self.date_input.value,
            TransactionValue=value_fmt.value,
        )

    def _on_form_update(self, widget: TextInput):
        """Actions performed when the user interacts with any input in the revenue
        form.
        """
        revenue = self._get_revenue_form_entry()
        if revenue.required_fields_are_filled():
            self._app.widgets["revenue_form_confirm"].enabled = True
        else:
            self._app.widgets["revenue_form_confirm"].enabled = False

    def _ensure_revenue_types(self):
        revenue_categories = ["Recebível À Vista", "Parcela De Recebível À Prazo"]
        current_data = [r.Name for r in self.revenue_type_source.current_data]
        for categ in revenue_categories:
            if categ not in current_data:
                rt = db.RevenueType(Name=categ)
                rt.write()
