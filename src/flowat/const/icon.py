from toga.icons import Icon
from toga.images import Image
from pathlib import Path
from PIL import Image as IMG

_RESOURCES_DIR = Path(Path(__file__).resolve().parent.parent, "resources")

CIRCLE_MINUS = Icon(path=Path(_RESOURCES_DIR, "circle-minus"), system=True)
CIRCLE_PLUS = Icon(path=Path(_RESOURCES_DIR, "circle-plus"), system=True)
SCAN_SEARCH = Icon(path=Path(_RESOURCES_DIR, "scan-search-32"), system=True)
MONEY_IN = Icon(path=Path(_RESOURCES_DIR, "money-in-32"), system=True)
MONEY_OUT = Icon(path=Path(_RESOURCES_DIR, "money-out-32"), system=True)
BAR_CHART = Icon(path=Path(_RESOURCES_DIR, "chart-column-32"), system=True)
SETTINGS = Icon(path=Path(_RESOURCES_DIR, "settings-32"), system=True)

with IMG.open(Path(_RESOURCES_DIR, "item-missing-symbolic-256.png")) as img:
    MISSING_ITEM_IMG = Image(img)
