from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flowat import config


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
    def invalid_reason(self) -> str:
        if not self._user_input:
            return f"'{self._field_name}' não pode ser vazio"


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
        numeric = (
            Decimal(self.value/100)
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        return f"{numeric:,.2f}".replace(",", " ").replace(".", ",")

    @property
    def invalid_reason(self) -> str | None:
        """Returns a string that explains the reason this input is invalid,
        or None otherwise.
        """
        super().invalid_reason()
        if self.value == 0:
            return f"'{self._field_name}' não pode ser zero"
        if self.value > config.MaxAllowedValue.get():
            return f"'{self._field_name}' acima do permitido"

    def is_valid(self) -> bool:
        """Verify if the integer is a valid input for currency."""
        return self.invalid_reason is None


class StringToBarcodeITF25(_Formatter):
    def __init__(self, user_input: str):
        """Checks if user_input string is a valid ITF-25 barcode."""
        self._user_input = user_input

    @property
    def invalid_reason(self) -> str | None:
        if not self._user_input.isdigit():
            return f"{self._field_name} deve conter apenas números"
        if len(self._user_input.strip()) not in [44, 47]:
            return f"Quantidade incorreta de caracteres em '{self._field_name}'"
