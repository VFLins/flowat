from toga.widgets.activityindicator import ActivityIndicator
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
from toga.platform import current_platform

from datetime import date, datetime
from typing import Any, Callable
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
    action1: str,
    action2: str,
    on_action1: Callable | None = None,
    on_action2: Callable | None = None,
    add_divider: bool = True,
) -> Box:
    button_style = (
        style.SIMPLE_SMALL_BUTTON
        if current_platform != "windows"
        else style.SIMPLE_BUTTON
    )
    rightmost_button_style = (
        style.RIGHTMOST_SIMPLE_SMALL_BUTTON
        if current_platform != "windows"
        else style.RIGHTMOST_SIMPLE_BUTTON
    )
    title_size = 12 if current_platform != "windows" else 11
    desc_size = 10 if current_platform != "windows" else 9
    container = Column(
        children=[
            Row(
                style=Pack(align_items="center", width=style.CONTENT_WIDTH - 1),
                children=[
                    Column(
                        children=[
                            Label(title, style=Pack(font_size=title_size)),
                            Label(description, style=Pack(font_size=desc_size)),
                        ]
                    ),
                    Box(style=Pack(flex=1)),
                    Button(action1, style=button_style, on_press=on_action1),
                    Button(action2, style=rightmost_button_style, on_press=on_action2),
                ],
            ),
        ]
    )
    if add_divider:
        container.add(Divider(style=Pack(margin_top=10, margin_bottom=10)))
    return container


class ReportSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
        self.example_item = report_entry(
            title="Exemplo de entrada",
            description="Uma descrição mais detalhada do que isso faz",
            action1="Ver",
            action2="Imprimir",
        )
        self.example_item2 = report_entry(
            title="Outro exemplo de entrada",
            description="Uma descrição mais detalhada do que isso faz",
            action1="Ver",
            action2="Imprimir",
            add_divider=False,
        )
        self.main_container = Column(children=[self.example_item, self.example_item2])
        self.full_contents = ScrollContainer(
            style=Pack(width=style.CONTENT_WIDTH), content=self.main_container
        )

    def show_main_content(self, widget: Button | None = None):
        """Removes currently displayed elments and show a summary of revenues."""
