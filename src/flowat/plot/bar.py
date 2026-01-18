import matplotlib.pyplot as plt
from PIL import Image
import io


def simple_columnplot(x: list[str], y: list[float], title: str | None = None) -> Image:
    plt.figure(figsize=(6, 4))
    plt.bar(x, y, color="#8d81ea")
    if title is not None:
        plt.title(title)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1, transparent=True)
    plt.close()  # Close the figure to free memory
    buf.seek(0)  # Rewind the buffer to the beginning
    return Image.open(buf)
