from toga.icons import Icon
from pathlib import Path


RESOURCES_DIR = Path(Path(__file__).resolve().parent.parent, "resources")

CIRCLE_MINUS = Icon(
    path=Path(RESOURCES_DIR, "circle-minus"), system=True
)
CIRCLE_PLUS = Icon(
    path=Path(RESOURCES_DIR, "circle-plus"), system=True
)
SCAN_SEARCH = Icon(
    path=Path(RESOURCES_DIR, "scan-search"), system=True
)
