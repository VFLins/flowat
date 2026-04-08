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


class ReportSection(BaseSection):
    def __init__(self, app):
        super().__init__(app=app)
