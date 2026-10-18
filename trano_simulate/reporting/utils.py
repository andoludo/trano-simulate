from pathlib import Path
from typing import TYPE_CHECKING, Any

from buildingspy.io.outputfile import Reader  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader

from trano_simulate.plot.plot import plot_figures, plot_plot_ly

if TYPE_CHECKING:
    from trano_simulate.reporting.reporting import ModelDocumentation

# autoescape is intentionally disabled: these templates render trusted internal
# data and the historical output was produced without escaping.
_TEMPLATES = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent.joinpath("templates"))),
    autoescape=False,  # noqa: S701
)


def to_html_space(data: dict[str, Any]) -> str:
    return _TEMPLATES.get_template("space.html").render(data=data)


def to_html_system(data: dict[str, Any]) -> str:
    return _TEMPLATES.get_template("system.html").render(data=data)


def to_html_construction(data: dict[str, Any]) -> str:
    return _TEMPLATES.get_template("construction.html").render(data=data)


def get_figures(element_name: str, documentation: "ModelDocumentation") -> list[Any]:
    """The plotly figures of an element, from the result file of the documentation."""
    if documentation.result is None:
        return []
    mat = Reader(documentation.result.path, documentation.result.type)
    return plot_figures(mat, documentation.description.figures.get(element_name, []), plot_plot_ly)
