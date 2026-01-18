import matplotlib.pyplot as plt
from PIL import Image
import io


def simple_barplot(x: list, y: list) -> Image:
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Sine Wave Plot")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)  # Close the figure to free memory
    buf.seek(0)  # Rewind the buffer to the beginning
    return Image.open(buf)
