from datetime import date
from dateutil.relativedelta import relativedelta

from toga.widgets.numberinput import NumberInput
from toga.widgets.selection import Selection
from toga.widgets.base import Widget
from toga.widgets.box import Row, Column
from toga.style import Pack

from flowat.const import style
from flowat.form.elem import FormField


class _TemplateBase:
    def __init__(self, container_style: Pack, fields: list[Widget]):
        pass
