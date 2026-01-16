from toga.icons import Icon
from pathlib import Path


_RESOURCES_DIR = Path(Path(__file__).resolve().parent.parent, "resources")

CIRCLE_MINUS = Icon(
    path=Path(_RESOURCES_DIR, "circle-minus"), system=True
)
CIRCLE_PLUS = Icon(
    path=Path(_RESOURCES_DIR, "circle-plus"), system=True
)
SCAN_SEARCH = Icon(
    path=Path(_RESOURCES_DIR, "scan-search"), system=True
)
MONEY_IN = Icon(
    path=Path(_RESOURCES_DIR, "money-in"), system=True
)
MONEY_OUT = Icon(
    path=Path(_RESOURCES_DIR, "money-out"), system=True
)
SETTINGS = Icon(
    path=Path(_RESOURCES_DIR, "settings"), system=True
)
