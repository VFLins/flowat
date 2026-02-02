from sys import platform
from datetime import datetime
import plotly.express as px
from plotly.graph_objects import Figure

from flowat.plot.base import PLOTLYJS_PATH
from flowat.const.sys import get_colors


def _set_layout(figure: Figure, x: list[str], y: list[float]) -> Figure:
    colors = get_colors()
    yticktext = [
        (
            f"R$ {v / 1000:.1f} mil".replace(".", ",")
            if v >= 1000
            else f"R$ {v:.2f}".replace(".", ",")
        )
        for v in y
    ]
    xticktext = [datetime.strptime(v, "%Y-%m").strftime("%b. %y").title() for v in x]
    return figure.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font={"color": colors["FG_COLOR"]},
        xaxis_title=None,
        xaxis={
            "tickmode": "array",
            "tickvals": x,
            "ticktext": xticktext,
            "fixedrange": True,
        },
        yaxis_title=None,
        yaxis={
            "tickmode": "array",
            "tickvals": y,
            "ticktext": yticktext,
            "fixedrange": True,
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        hovermode="x unified",
        barcornerradius=6,
    )


def colplot(x: list[str], y: list[float]) -> str:
    bg_color = get_colors()["BG_COLOR"]
    fig = px.bar(x=x, y=y)
    fig = _set_layout(figure=fig, x=x, y=y)
    fig.update_traces(hovertemplate=None, marker_color="#8d81ea")
    fig.update_yaxes(showticklabels=False, showgrid=False)
    transparent_bg = f"document.body.style.backgroundColor = '{bg_color}';"
    if platform in ["win32", "android"]:
        html = fig.to_html(
            include_plotlyjs="cdn",
            post_script=[transparent_bg],
            config={"displayModeBar": False},
        )
    else:
        html = fig.to_html(
            include_plotlyjs=PLOTLYJS_PATH,
            post_script=[transparent_bg],
            config={"displayModeBar": False},
        )
    return html
