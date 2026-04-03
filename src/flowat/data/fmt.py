from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from datetime import datetime

from flowat import config


class _Manipulator:
    def __init__(self, value: Any):
        self._value = value


class _Parser:
    def __init__(self, formatted_value: Any):
        self._formatted_value = formatted_value

    @property
    def presumed_input(self):
        return str(self._formatted_value)


class _Formatter:
    def __init__(self, user_input: str, field_name: str):
        self._user_input, self._field_name = user_input, field_name

    @property
    def value(self) -> str:
        if self.is_valid():
            return self._user_input
        else:
            return ""

    @property
    def invalid_reason(self) -> str | None:
        if not self._user_input:
            return f"'{self._field_name}' não pode ser vazio"

    def is_valid(self) -> bool:
        """Verify if the integer is a valid input for currency."""
        return self.invalid_reason is None


class CurrencyToString(_Parser):
    @property
    def presumed_input(self) -> str:
        return f"{self._formatted_value / 100}".replace(".", ",")


class StringToCurrency(_Formatter):
    @property
    def value(self) -> int:
        """Convert the currency inserted by the user in a text field to an integer.
        This integer preserves two decimal places, so 100 should be interpreted as R$ 1.
        """
        try:
            return int(Decimal(self._user_input.replace(",", ".")) * 100)
        except InvalidOperation:
            return 0

    @property
    def display_value(self) -> str:
        """Format the user input to be displayed on the UI."""
        numeric = Decimal(self.value / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return f"{numeric:,.2f}".replace(",", " ").replace(".", ",")

    @property
    def invalid_reason(self) -> str | None:
        """Returns a string that explains the reason this input is invalid,
        or None otherwise.
        """
        super().invalid_reason

        if self.value == 0:
            return f"'{self._field_name}' não pode ser zero"
        if self.value > config.MaxAllowedValue.get():
            return f"'{self._field_name}' acima do permitido"


class StringFullDateTime(_Manipulator):
    def __init__(self, value: str):
        super().__init__(value=value)
        self._parsed_value: datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")

    @property
    def date(self):
        return self._parsed_value.strftime("%d/%m/%Y")

    @property
    def time(self):
        return self._parsed_value.strftime("%H:%M:%S")

    @property
    def datetime(self):
        return self._parsed_value.strftime("%d/%m/%Y às %H:%M")


class StringToBarcodeITF25(_Formatter):
    @property
    def invalid_reason(self) -> str | None:
        if not self._user_input.isdigit():
            return f"{self._field_name} deve conter apenas números"
        if len(self._user_input.strip()) not in [44, 47]:
            return f"Quantidade incorreta de caracteres em '{self._field_name}'"
