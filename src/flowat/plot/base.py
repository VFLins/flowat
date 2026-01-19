from plotly.offline import get_plotlyjs
from pathlib import Path

from flowat.const.sys import FLOWAT_FILES_PATH


PLOTLYJS_PATH = Path(FLOWAT_FILES_PATH, "plotly.min.js")

def ensure_plotlyjs():
    if not PLOTLYJS_PATH.is_file():
        js_content = get_plotlyjs()
        print("Writing plotly.min.js file...")
        with open("plotly.min.js", "w", encoding="utf-8") as f:
            f.write(js_content)
