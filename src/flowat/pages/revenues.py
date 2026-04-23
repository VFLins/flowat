from toga.widgets.activityindicator import ActivityIndicator
from toga.widgets.imageview import ImageView
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.webview import WebView
from toga.widgets.button import Button
from toga.widgets.switch import Switch
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Column, Row
from toga.widgets.optioncontainer import OptionContainer
from toga.widgets.scrollcontainer import ScrollContainer
from toga.dialogs import InfoDialog, ConfirmDialog, SelectFolderDialog
from toga.style import Pack
from toga.platform import current_platform

from datetime import date, datetime
from typing import Any
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
    SELECTED_SELLER = nf.TableName("")  # TODO: Read from config
    REVENUE_CATEGORIES = [
        "Recebível À Vista",
        "Parcela De Recebível À Prazo",
        "Documento Escaneado",
    ]
    HIDDEN_REVENUE_CATEGORIES = ["Documento Escaneado"]
    revenues_source = source.RevenuesSource()
    agg_revenues_source = source.AggregatedRevenuesSource()
    revenue_type_source = source.RevenueTypeSource()

    def __init__(self, app):
        super().__init__(app=app)
        self._ensure_revenue_types()
        self.plot_revenue = WebView(
            style=Pack(width=515, height=120),
            on_webview_load=self._on_reload_plot,
        )
        self.date_input = HorizontalDateForm(value=date.today())
        self.value_input = TextInput(
            style=Pack(width=int(style.FORM_WIDTH / 3)),
            placeholder="0,00",
            on_change=self._on_form_update,
        )
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
        self.scanner_image = ImageView(
            image=icon.SCANNER_IMG,
            style=Pack(margin_bottom=20, width=96, height=96),
        )
        self.scan_docs_button = FormField(
            label="Ações",
            input_widget=Button(
                text="Escanear uma pasta",
                style=style.user_input(Button),
                on_press=self.nflogic_scan,
            ),
            description="Escaneia dados dos arquivos\nde uma pasta",
        )
        self.select_scanned_revenues_button = FormField(
            label="",
            input_widget=Button(
                "Selecionar dados", on_press=self.select_scanned_revenues
            ),
            description="Seleciona dados disponíveis\npara inserir",
        )
        self.add_scanned_data_button = Button(
            "Inserir",
            style=style.RIGHTMOST_SIMPLE_BUTTON,
            enabled=False,
            on_press=self.add_selected_revenues,
        )
        self.selected_scanned_revenues_table = Table(
            multiple_select=True,
            style=Pack(width=style.FORM_WIDTH, flex=1),
            headings=["Valor", "Data"],
            on_select=self._scanned_revenue_data_selection,
        )
        self.select_all_scanned_revenues_switch = Switch(
            "Selecionar tudo",
            on_change=self.change_scanned_revenues_selection,
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
        self.revenue_input_form_content = Column(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[
                FormField(
                    id="revenue_form_type",
                    container_style=Pack(width=style.FORM_WIDTH),
                    input_widget=Selection(
                        on_change=self._on_form_update,
                        items=[
                            r
                            for r in self.REVENUE_CATEGORIES
                            if r not in self.HIDDEN_REVENUE_CATEGORIES
                        ],
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
                FormField(
                    id="expense_form_value",
                    container_style=Pack(width=style.FORM_WIDTH),
                    input_widget=self.value_input,
                    label="Valor",
                    unstyled=True,
                ),
                Row(
                    style=Pack(
                        width=style.FORM_WIDTH, align_items="end", margin_top=20
                    ),
                    children=[
                        Box(style=Pack(flex=1)),  # push buttons to the right side
                        Button(
                            "Voltar",
                            style=style.SIMPLE_BUTTON,
                            on_press=self.show_main_content,
                        ),
                        Button(
                            "Inserir",
                            id="revenue_form_confirm",
                            enabled=False,
                            style=style.RIGHTMOST_SIMPLE_BUTTON,
                            on_press=self.add_revenue,
                        ),
                    ],
                ),
            ],
        )
        self.revenue_input_form = ScrollContainer(
            content=self.revenue_input_form_content
        )
        self.scan_status_section = Row(
            style=Pack(align_items="center"),
            children=[self.scan_activity, self.scan_info],
        )
        self.revenue_scan_form_head = Column(
            style=Pack(align_items="center", margin_top=20),
            children=[
                self.scanner_image,
                self.scan_status_section,
            ],
        )
        self.revenue_scan_form_step1 = Row(
            children=[self.scan_docs_button, self.select_scanned_revenues_button],
        )
        self.revenue_scan_form_step2 = FormField(
            label="",
            container_style=style.CENTERED_MAIN_CONTAINER,
            input_widget=Table(
                style=Pack(width=style.FORM_WIDTH, flex=1),
                accessors=["name"],
                on_activate=self._on_select_seller_name,
            ),
            unstyled=True,
        )
        self.revenue_scan_form_step3 = FormField(
            label="",
            container_style=style.CENTERED_FORM_SECTION,
            input_widget=Column(
                style=style.FORM_SECTION,
                children=[
                    self.select_all_scanned_revenues_switch,
                    self.selected_scanned_revenues_table,
                    Row(
                        style=Pack(width=style.FORM_WIDTH),
                        children=[
                            Box(style=Pack(flex=1)),  # push buttons to the right side
                            Button(
                                "Voltar",
                                style=style.SIMPLE_BUTTON,
                                on_press=self.show_main_content,
                            ),
                            self.add_scanned_data_button,
                        ],
                    ),
                ],
            ),
            unstyled=True,
        )
        self.revenue_scan_form_content = Column(
            style=style.CENTERED_MAIN_CONTAINER,
            children=[
                self.revenue_scan_form_head,
                self.revenue_scan_form_step1,
            ],
        )
        self.revenue_scan_form = ScrollContainer(content=self.revenue_scan_form_content)
        self.revenue_form = OptionContainer(
            style=style.MAIN_CONTAINER,
            content=[
                ("Inserção manual", self.revenue_input_form),
                ("Escanear notas de venda", self.revenue_scan_form),
            ],
        )
        self.main_container = Box(
            children=[self.first_interaction],
        )
        """Holds any interactive container of this section and handles vertical
        alignment. It's styling is defined externally via function call.
        """
        self.full_contents = Box(
            children=[self.main_container],
        )
        """Always holds only `RevenuesSection.main_container` and handles horizontal
        alignment. This is the highest level container.
        """
        self._refresh_displayed_data()

    def show_form(self, widget: Button):
        """Removes currently displayed elments and show a form where the user can
        add a new revenue.
        """
        self.main_container.clear()
        self.main_container.add(self.revenue_form)
        self.main_container.style = Pack(align_items="center", direction="row")
        asyncio.create_task(self._check_available_scanned_data())

    def show_main_content(self, widget: Button | None = None):
        """Removes currently displayed elments and show a summary of revenues."""
        self._reset_scanned_revenue_form()
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
        def stop_activity_indicator(task: asyncio.Task):
            _ = task
            self.scan_activity.stop()
            self.add_scanned_data_button.enabled = True
        result = task.result()
        print(f"INFO: User selected directory for scanning: {result}")
        if result:
            self.scan_activity.start()
            self.scan_info.text = "Processando documentos, aguarde..."
            self.add_scanned_data_button.enabled = False
            task = asyncio.create_task(self._scan_documents(dir_path=result))
            task.add_done_callback(stop_activity_indicator)

    async def _check_available_scanned_data(self):
        """Allows the user to add scanned data if any is available, forbids otherwise."""
        self.select_scanned_revenues_button.input.enabled = False
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
        if acm_count == 0:
            self.scan_info.text = "Nenhum dado disponível para inserir."
        else:
            self.scan_info.text = f"Dados de {acm_count} documentos encontrados."
            self.select_scanned_revenues_button.input.enabled = True
        self.scan_activity.stop()

    async def _scan_documents(self, dir_path: str):
        """Handles user interaction when adding data from processed documents."""
        def parse_dir():
            return nflogic.parse_dir(dir_path=dir_path, buy=False, full_parse=False)
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, parse_dir)
        finally:
            asyncio.create_task(self._check_available_scanned_data())

    def select_scanned_revenues(self, widget: Button):
        """Guides the user into selecting the desired subset of the scanned data."""
        seller_names = nf.get_seller_names()
        self.revenue_scan_form_head.remove(self.scanner_image)
        if len(seller_names) > 1:
            self.scan_info.text = "Escolha o nome do vendedor com um clique duplo"
            self.revenue_scan_form_step2.input.data = seller_names
            self.revenue_scan_form_content.remove(self.revenue_scan_form_step1)
            self.revenue_scan_form_content.add(self.revenue_scan_form_step2)
        else:
            self._load_seller_data(seller_name=seller_names[0])

    def add_selected_revenues(self, widget: Button):
        """Adds any data from the selected seller name to the database."""
        new_data = self.selected_scanned_revenues_table.selection
        if not new_data:
            return
        for row in new_data:
            data = nf.get_processed_document(
                seller_name=self.SELECTED_SELLER, row_id=row.id
            )
            print(f"INFO: adding transaction {row}")
            revenue = db.RevenueEntry(
                IdRevenueType=3,
                TimeStamp=datetime.now(),
                Description="Receita",
                TransactionDate=fmt.StringFullDateTime(data.DataHoraEmi).parsed_value,
                TransactionValue=data.TotalProdutos,
            )
            revenue.write()
            scanned_ref = db.ScannedInvoiceFile(
                DocumentIdentifier=data.ChaveNFe,
                IdRevenueEntry=revenue.Id,
            )
            scanned_ref.write()
        self._refresh_displayed_data()
        self.show_main_content(widget=widget)

    def _on_select_seller_name(self, widget: Table, row: Any, **kwargs):
        """Sends the user to a confirmation step, where new revenue data from the
        selected seller is displayed.
        """
        self._load_seller_data(seller_name=row.name)

    def _load_seller_data(self, seller_name: nf.TableName):
        """Prepares the selected set of revenue data to be inserted."""
        self.SELECTED_SELLER = seller_name
        self.scan_info.text = (
            "Revise as transações que serão adicionadas,\n"
            'clique "Inserir" para confirmar'
        )
        table = self.selected_scanned_revenues_table
        form = self.revenue_scan_form_content
        table.data = [
            {
                "id": r.Id,
                "valor": f"{r.TotalProdutos:.2f}".replace(".", ","),
                "data": fmt.StringFullDateTime(r.DataHoraEmi).datetime,
            }
            for r in nf.get_new_seller_data(seller_name=seller_name)
        ]
        form.remove(self.revenue_scan_form_step1)
        form.remove(self.revenue_scan_form_step2)
        form.add(self.revenue_scan_form_step3)
        self._select_all_rows(table=table)
        self.select_all_scanned_revenues_switch.value = True
        self.add_scanned_data_button.enabled = len(table.data) > 0

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
        else:
            self.plot_revenue.content = colplot(x=[], y=[])

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
        else:
            self.plot_revenue.content = colplot(x=[], y=[])

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
        # scanned data
        self._reset_scanned_revenue_form()
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

    def _reset_scanned_revenue_form(self):
        """Returns the 'scanned revenues' form to it's initial state."""
        self.revenue_scan_form_content.remove(self.revenue_scan_form_step2)
        self.revenue_scan_form_content.remove(self.revenue_scan_form_step3)
        self.revenue_scan_form_content.add(self.revenue_scan_form_step1)
        self.revenue_scan_form_head.clear()
        self.revenue_scan_form_head.add(self.scanner_image, self.scan_status_section)
        self.add_scanned_data_button.enabled = False

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
        current_data = [r.Name for r in self.revenue_type_source.current_data]
        for categ in self.REVENUE_CATEGORIES:
            if categ not in current_data:
                rt = db.RevenueType(Name=categ)
                rt.write()

    def change_scanned_revenues_selection(self, widget: Switch):
        table = self.selected_scanned_revenues_table
        if widget.value:
            self._select_all_rows(table=table)
        else:
            self._unselect_all_rows(table=table)
        print(table.selection)

    def _select_all_rows(self, table: Table):
        native_table = table._impl.native
        match current_platform:
            case "linux":
                selection = native_table.get_child().get_selection()
                selection.select_all()
            case "windows":
                for i in range(native_table.Items.Count):
                    native_table.Items[i].Selected = True
            case _:
                raise NotImplementedError(
                    f"Select all rows from table is unsupported on {current_platform=}"
                )

    def _unselect_all_rows(self, table: Table):
        native_table = table._impl.native
        match current_platform:
            case "linux":
                native_table.get_child().get_selection().unselect_all()
            case "windows":
                native_table.SelectedIndices.Clear()
            case _:
                raise NotImplementedError(
                    f"Unselect all rows from table is unsupported on {current_platform=}"
                )

    def _scanned_revenue_data_selection(self, widget: Table):
        self.add_scanned_data_button.enabled = len(widget.selection) > 0
