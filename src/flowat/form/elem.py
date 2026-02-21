from typing import Iterable, Callable, Type, Literal
from decimal import Decimal
import asyncio

from toga.style import Pack
from toga.widgets.box import Box, Column
from toga.widgets.base import Widget
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.numberinput import NumberInput
from toga.widgets.detailedlist import DetailedList

from flowat.const import style


class Heading(Box):
    """A modified `toga.Box` that includes children and properties:

    - :label: A `toga.Label` styled as a heading
    - :divider: A `toga.Divider`
    """

    def __new__(self, label: str, level: Literal[1, 2] = 1, id: str | None = None):
        label_widget = Label(
            text=label,
            id=f"{id}_label" if id else f"{label}_label" if label else None,
            style=style.HEADING2 if level == 2 else style.HEADING1,
        )
        divider = Divider()
        self.contents = Column(children=[label_widget, divider])
        self.contents.label = label_widget
        self.contents.divider = divider
        return self.contents


class FormField(Box):
    """A modified `toga.Box` that includes children and properties:

    - :label: A `toga.Label` positioned above the input that holds the input title;
    - :input: The `input_widget` provided, should be a Toga widget that accepts user input;
    - :description: An extra `toga.Label` positioned below the input with extra information
      about it, will only be present if `description` is provided.
    - :id: `id` to be assigned to the parent widget, it's children can be accessed as
      properties [label, input, description];
    - :is_required: Metadata indicating if this is a required field, can be accessed as
      a property and can be useful to validation logic;
    - :container_style: Styling defined to the parent container, should be used only
      when trying to override the default behavior;
    - :unstyled: If `True`, indicates if the input_widget should use it's own provided
      styling, uses the default style by it's input type otherwise.
    """

    def __new__(
        self,
        label: str,
        input_widget: Widget,
        description: str | None = None,
        id: str | None = None,
        is_required: bool = False,
        container_style: Pack | None = None,
        unstyled: bool = False,
    ):
        label_widget = Label(
            text=label,
            id=f"{id}_label" if id else f"{label}_label" if label else None,
            style=style.input_annotation(),
        )
        self.contents = Column(
            style=container_style if container_style else None,
            id=id if id else label,
            children=[label_widget, input_widget],
        )
        if not unstyled:
            input_widget.style = style.user_input(type(input_widget))
        if description:
            description_widget = Label(
                text=description,
                id=f"{id}_desc" if id else f"{label}_desc" if label else None,
                style=style.input_annotation("legend"),
            )
            self.contents.add(description_widget)
            self.contents.description = description_widget
        self.contents.label = label_widget
        self.contents.input = input_widget
        self.contents.is_required = is_required
        return self.contents
