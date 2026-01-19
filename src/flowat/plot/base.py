from plotly.offline import get_plotlyjs
from pathlib import Path

from toga.paths import Paths as appdir


PLOTLYJS_PATH = Path(appdir().data, "plotly.min.js")

def ensure_plotlyjs():
    if not PLOTLYJS_PATH.is_file():
        print("Writing plotly.min.js file...")
        with open("plotly.min.js", "w", encoding="utf-8") as f:
            f.write(js_content)
