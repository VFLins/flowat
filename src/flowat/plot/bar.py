import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.patches import FancyBboxPatch
from matplotlib.path import Path
import matplotlib.patches as patches
import plotly.express as px
from PIL import Image
import io

from flowat.plot.base import PLOTLYJS_PATH
from flowat.const.sys import BG_COLOR, FG_COLOR


def get_rounded_bar(x, y, width, radius):
    """Cria um caminho (Path) para uma barra com topo arredondado."""
    # Se o raio for maior que a metade da largura ou altura, ajustamos
    radius = min(radius, width/2, y)
    # Comandos do caminho: MOVETO, LINETO, CURVE4 (para os cantos)
    verts = [
        (x - width/2, 0),                       # Base esquerda
        (x - width/2, y - radius),              # Início da curva superior esquerda
        (x - width/2, y), (x - width/2 + radius, y), # Curva superior esquerda (bezier)
        (x + width/2 - radius, y),              # Linha reta superior
        (x + width/2, y), (x + width/2, y - radius), # Curva superior direita (bezier)
        (x + width/2, 0),                       # Base direita
        (x - width/2, 0),                       # Fecha o caminho
    ]
    codes = [
        Path.MOVETO, Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO, Path.CLOSEPOLY,
    ]
    return Path(verts, codes)


def simple_columnplot(x: list[str], y: list[float], title: str | None = None) -> Image:
    # 1. gráfico
    plt.figure(figsize=(7, 3))
    bars = plt.bar(x, y, color="#8d81ea")
    if title is not None:
        plt.title(title)
    # 2. remover bordas
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tick_params(axis='y', which='both', left=False, labelleft=False)
    plt.tick_params(axis='x', which='both', length=0, pad=10)
    ax.set_xticklabels(x, fontweight='bold', color="White")
    # 4. legendas nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height}', ha='center', va='bottom', 
                 fontsize=10, fontweight='bold', color='#2e4053')
    plt.draw() # Força o desenho para garantir que os labels existam antes de editá-los
    trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transAxes)
    rect_bg = FancyBboxPatch(
        (0.02, -0.15), 0.96, 0.12, transform=trans, 
        boxstyle="round,pad=0.03,rounding_size=0.08",
        color="#a8a8a8", zorder=1, clip_on=False
    )
    ax.add_patch(rect_bg)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1, transparent=True)
    plt.close()  # Close the figure to free memory
    buf.seek(0)  # Rewind the buffer to the beginning
    return Image.open(buf)


def interactive_columnplot(x: list[str], y: list[float]) -> str:
    fig = px.bar(x=x, y=y)
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font={"color": FG_COLOR},
    )
    transparent_bg = f"document.body.style.backgroundColor = '{BG_COLOR}';"
    html = fig.to_html(include_plotlyjs=PLOTLYJS_PATH, post_script=[transparent_bg])
    return html
