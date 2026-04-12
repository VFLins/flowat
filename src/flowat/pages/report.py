from toga.widgets.activityindicator import ActivityIndicator
from toga.widgets.numberinput import NumberInput
from toga.widgets.imageview import ImageView
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.webview import WebView
from toga.widgets.divider import Divider
from toga.widgets.button import Button
from toga.widgets.switch import Switch
from toga.widgets.table import Table
from toga.widgets.label import Label
from toga.widgets.box import Box, Column, Row
from toga.widgets.optioncontainer import OptionContainer
from toga.widgets.scrollcontainer import ScrollContainer
from toga.dialogs import InfoDialog, ConfirmDialog, SelectFolderDialog
from toga.style import Pack
from toga.icons import Icon
from toga.platform import current_platform

from datetime import date, datetime
from typing import Any, Callable, Literal
import asyncio
import nflogic

from .base import BaseSection

from flowat.data import db, source, fmt, nf
from flowat.const import icon, style
from flowat.plot.bar import colplot
from flowat.form.elem import FormField
from flowat.form.date import HorizontalDateForm


def report_entry(
    title: str,
    description: str,
    action_face: str | Icon,
    on_action: Callable | None = None,
    add_divider: bool = True,
) -> Box:
    title_size = 11
    desc_size = 9
    content_width = style.CONTENT_WIDTH - 1
    button_style = Pack(font_weight="bold", font_size=title_size)
    if isinstance(action_face, str):
        action_button = Button(action_face, style=button_style, on_press=on_action)
    else:
        action_button = Button(icon=action_face, style=button_style, on_press=on_action)
    annotations = Column(
        children=[
            Label(title, style=Pack(font_size=title_size, font_weight="bold")),
            Label(description, style=Pack(font_size=desc_size)),
        ]
    )
    container = Column(
        children=[
            Row(
                style=Pack(align_items="center", width=content_width),
                children=[annotations, Box(style=Pack(flex=1)), action_button],
            ),
        ]
    )
    if add_divider:
        container.add(Divider(style=Pack(margin=(10, 0), width=content_width)))
    return container


def report_screen(data_source: source._DataSource | None, page: BaseSection) -> Box:
    def change_view(widget: Selection):
        canvas.clear()
        match widget.value:
            case "Gráfico":
                canvas.add(data_widget("plot"))
            case _:
                canvas.add(data_widget("table"))

    def print_canvas_content(widget: Button):
         print("canvas content, wow")

    def data_widget(type: Literal["plot", "table"]) -> WebView | Table:
        s = Pack(flex=1, width=style.FORM_WIDTH, height=style.FORM_WIDTH * 0.6)
        match type:
            case "plot":
                plot = colplot(x=[], y=[])
                return WebView(style=s, content=plot)
            case _:
                return Table(style=s, headings=["Data", "Exemplo"])

    return_button = Button("Voltar", on_press=lambda w: page.show_main_content())
    print_button = Button("Imprimir", on_press=print_canvas_content)
    select_view = FormField(
        label="Tipo",
        input_widget=Selection(items=["Tabela", "Gráfico"], on_change=change_view)
    )
    select_freq = FormField(
        label="Frequência",
        input_widget=Selection(style=Pack(margin=(0, 5)), items=["Mensal", "Semanal"])
    )
    sample_size = FormField(
        label="Quantidade",
        input_widget=NumberInput(value=6, min=1, max=52, step=1),
    )
    header = Row(
        style=Pack(margin_bottom=10, align_items="end"),
        children=[select_view, select_freq, Box(style=Pack(flex=1)), print_button]
    )
    canvas = Column(style=Pack(align_items="center"), children=[data_widget("table")])
    footer = Row(
        style=Pack(margin_bottom=20, align_items="end"),
        children=[sample_size, Box(style=Pack(flex=1)), return_button]
    )
    return Column(
        style=Pack(width=style.CONTENT_WIDTH, align_items="center"),
        children=[header, canvas, footer]
    )



class ReportSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
        self.report_balance_entry = report_entry(
            title="Balanço financeiro",
            description="Fluxo de entradas e saídas do caixa, com saldo mensal",
            action_face=">",
            on_action=self.show_balance_content,
        )
        self.report_topay_entry = report_entry(
            title="Próximas contas à pagar",
            description="Relação de dívidas com vencimento próximo",
            action_face=">",
        )
        self.report_avgticket_entry = report_entry(
            title="Ticket médio",
            description="Valor médio das entradas no caixa",
            action_face=">",
            add_divider=False,
        )
        self.balance_screen = report_screen(data_source=None, page=self)
        self.report_options = Column(
            children=[
                self.report_balance_entry,
                self.report_topay_entry,
                self.report_avgticket_entry,
            ]
        )
        self.main_container = Box(children=[self.report_options])
        self.full_contents = ScrollContainer(
            style=Pack(width=style.CONTENT_WIDTH), content=self.main_container
        )

    def show_main_content(self, widget: Button | None = None):
        """Removes currently displayed elments and show a summary of revenues."""
        self.main_container.clear()
        self.main_container.add(self.report_options)

    def show_balance_content(self, widget: Button | None = None):
        self.main_container.clear()
        self.main_container.add(self.balance_screen)

