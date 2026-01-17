from typing import Iterable, Callable, Type
from decimal import Decimal
import asyncio

from toga.style import Pack
from toga.widgets.box import Box, Column
from toga.widgets.base import Widget
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.numberinput import NumberInput
from toga.widgets.detailedlist import DetailedList

from flowat.const.style import input_annotation, user_input

class _LabeledInput:
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Base class for creating input fields with labels. Get the generated Box by
        accessing :ref::`_LabeledInput.widget`.

        :type label_text: ``str``
        :param label_text: Text displayed on the `toga.Label` widget. This widget
            can be accessed from `_LabeledInput.label`.
        :type id: ``str`` | ``None``
        :param id: The ID for the widget.
        :type style: ``Pack`` | ``None``
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :type kwargs: ``Any``
        :param kwargs: Keyword arguments passed to the equivalent `_LabeledInput.input` widget.
        """
        self.label = Label(
            text=label_text, id=id + "_label" if id else None, style=input_annotation()
        )
        self._set_input(id=id + "_input" if id else None, style=style, **kwargs)
        self.widget = Column(id=id, style=style, children=[self.label, self.input])

    def _set_input(self, id, style, **kwargs):
        """Used by `_LabeledInput`'s children to define the input widget.

        :param id: Used by `self.__init__()` to define input widget's ID.
        :param kwargs: Arguments fowarded from `self.__init__()`to the input widget.
        """
        self.input = TextInput(id=id, style=style, **kwargs)

    @property
    def value(self) -> object:
        """Provides direct access to `self.input.value`, allowing this class to mimic
        it's behavior.
        """
        return self.input.value

    @value.setter
    def value(self, value: object):
        self.input.value = value

    @property
    def on_change(self) -> Callable:
        """Provides direct access to `self.input.on_change`, allowing this class to mimic
        it's behavior.
        """
        return self.input.on_change

    @on_change.setter
    def on_change(self, func: Callable):
        self.input.on_change = func


class LabeledNumberInput(_LabeledInput):
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Implementation of `toga.NumberInput` with a static label on top.

        :param label_text: Text displayed on the `toga.Label` widget.
        :param id: The ID for `self.widget`.
        :param kwargs: Arguments passed to :ref:`toga.NumberInput`.
        """
        super().__init__(label_text, id, style, **kwargs)

    def _set_input(self, id, style, **kwargs):
        self.input = NumberInput(id=id, style=style, **kwargs)

    @property
    def max(self) -> Decimal | None:
        """Provides direct access to `self.input.max`, allowing this class to mimic
        it's behavior.
        """
        return self.input.max

    @max.setter
    def max(self, value: Decimal):
        self.input.max = value

    @property
    def min(self) -> Decimal | None:
        """Provides direct access to `self.input.min`, allowing this class to mimic
        it's behavior.
        """
        return self.input.min

    @min.setter
    def min(self, value: Decimal):
        self.input.min = value

    @property
    def step(self) -> Decimal:
        """Provides direct access to `self.input.step`, allowing this class to mimic
        it's behavior.
        """
        return self.input.step

    @step.setter
    def step(self, value: Decimal):
        self.input.step = value


class LabeledSelection(_LabeledInput):
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Implementation of `toga.Selection` with a static label on top.

        :param label_text: Text displayed on the `toga.Label` widget.
        :param id: The ID for `self.widget`.
        :param kwargs: Arguments passed to :ref:`toga.Selection`.
        """
        super().__init__(label_text, id, style, **kwargs)

    def _set_input(self, id, style, **kwargs):
        self.input = Selection(id=id, style=style, **kwargs)

    @property
    def items(self):
        """Provides direct access to `self.input.items`, allowing this class to mimic
        it's behavior.
        """
        return self.input.items

    @items.setter
    def items(self, items: Iterable | None):
        self.input.items = items


class FormField(Box):
    """A modified `toga.Box` that includes children and properties:

    - :label: A `toga.Label` positioned above the input that holds the input title;
    - :input: The `input_widget` provided, should be a Toga widget that accepts user input;
    - :description: An extra `toga.Label` positioned below the input with extra information
      about it, will only be present if `description` is provided.
    """

    def __new__(
        self,
        label: str,
        input_widget: Type[Widget],
        description: str | None = None,
        id: str | None = None,
        is_required: bool = False,
        **kwargs,
    ):
        label_widget = Label(
            text=label,
            id=f"{id}_label" if id else f"{label}_label",
            style=input_annotation(),
        )
        input_widget.style = user_input(type(input_widget))

        self.contents = Box(
            id=id if id else label,
            style=Pack(direction="column"),
            children=[label_widget, input_widget],
        )
        if description:
            description_widget = Label(
                text=description,
                id=f"{id}_desc" if id else f"{label}_desc",
                style=input_annotation("legend"),
            )
            self.contents.add(description_widget)
            self.contents.description = description_widget

        self.contents.label = label_widget
        self.contents.input = input_widget
        self.contents.is_required = is_required
        return self.contents


