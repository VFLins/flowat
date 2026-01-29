from plotly.offline import get_plotlyjs
from pathlib import Path
import datetime
import locale

from flowat.const.sys import FLOWAT_FILES_PATH

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
PLOTLYJS_PATH = Path(FLOWAT_FILES_PATH, "plotly.min.js")


def ensure_plotlyjs():
    if not PLOTLYJS_PATH.is_file():
        js_content = get_plotlyjs()
        print("Writing plotly.min.js file...")
        with open(PLOTLYJS_PATH, "w", encoding="utf-8") as f:
            f.write(js_content)


def month_labels(date: datetime.date, months: int) -> list[str]:
    """Generate a list of month labels starting from `date`'s month."""
    y, m, d = date.timetuple()[:3]
    return [
        datetime.date(year=int(y + ((m + i) / 12)), month=((m + i) % 12) or 12, day=1)
        .strftime("%b. %Y")
        .title()
        for i in range(months)
    ]
