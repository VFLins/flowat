from typing import Type, Literal
from sys import platform

from toga.style import Pack
from toga.widgets.base import Widget
from toga.widgets.button import Button
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.numberinput import NumberInput


CONTENT_WIDTH = 440

# containers
CENTERED_MAIN_CONTAINER = Pack(
    align_items="center", flex=1, direction="row", margin=(0, 0, 20, 0)
)
MAIN_CONTAINER = Pack(align_items="center", direction="column", width=440, margin=(0, 0, 20, 0))

# labels
HEADING1 = Pack(font_size=14, font_weight="bold", margin=(15, 0, 0, 0))
HEADING2 = Pack(font_size=11, font_weight="bold", font_style="italic", margin=(10, 0, 0 ,0))

# buttons
BIG_BUTTON = Pack(width=220, margin=5)
BIG_SQUARE_BUTTON = Pack(width=52, height=52, margin=5)

def user_input(widget_type: Type[Widget]) -> Pack:
    """Returns the default style for the user input's form element."""
    if widget_type in [TextInput, Button]:
        return Pack(margin=(0, 5), width=190)
    elif widget_type is NumberInput:
        return _system_based_number_input_style()
    elif widget_type is Selection:
        return _system_based_selection_style()
    else:
        return Pack()


def input_annotation(annotation_type: Literal["label", "legend"] = "label") -> Pack:
    """Returns the default style for the user input's annotation element."""
    if annotation_type == "label":
        return _system_based_input_label_style()
    elif annotation_type == "legend":
        return Pack(font_size=10, margin=(0, 0, 10, 5))
    else:
        raise ValueError(f"{annotation_type=}, expected one of 'label', 'legend'.")


def number_input_width():
    if platform == "linux":
        return 130
    return 70


def selection_width():
    if platform == "linux":
        return 140
    return 120


def _system_based_input_label_style() -> Pack:
    """OS based style for a `toga.Label` element used as label to an input field."""
    if platform == "linux":
        return Pack(margin=(15, 5, 2, 8))
    else:
        return Pack(margin=(25, 5, 2, 2))


def _system_based_selection_style() -> Pack:
    """OS based style for a `toga.Selection` element used as form input field."""
    if platform == "linux":
        return Pack(margin=(0, 5, 0, 8), width=110)
    else:
        return Pack(margin=(0, 5), width=110)


def _system_based_number_input_style() -> Pack:
    """OS based style for a `toga.NumberInput` element used as form input field."""
    if platform == "linux":
        return Pack(margin=(0, 5), width=number_input_width())
    else:
        return Pack(margin=(0, 5), width=number_input_width())
