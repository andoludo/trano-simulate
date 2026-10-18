"""Reports from the description of a model (written by trano) and its result file, without trano."""

from pathlib import Path

import matplotlib
import pytest
from buildingspy.io.outputfile import Reader  # type: ignore[import-untyped]

from trano_simulate.plot import NamedFigure, plot, plot_figures, plot_plot_ly, plot_plot_ly_many
from trano_simulate.reporting import (
    ContentDocumentation,
    ContentModelDocumentation,
    ModelDescription,
    ModelDocumentation,
    ResultFile,
    to_docx,
    to_html_reporting,
)
from trano_simulate.reporting.utils import get_figures

matplotlib.use("Agg")

RESOURCES = Path(__file__).parent / "resources"
DESCRIPTION = RESOURCES / "two_rooms.description.json"
RESULT = RESOURCES / "data.mat"


@pytest.fixture
def description() -> ModelDescription:
    return ModelDescription.read(DESCRIPTION)


def test_the_description_is_read_back_as_written(description: ModelDescription, tmp_path: Path) -> None:
    path = description.write(tmp_path / "copy.description.json")

    assert ModelDescription.read(path) == description
    assert description.name == "buildings_two_rooms_with_storage"
    assert [space["name"] for space in description.spaces] == ["space_1", "space_2"]
    assert list(description.space_figures) == ["space_1", "space_2"]


def test_the_documentation_tables_come_from_the_description(description: ModelDescription) -> None:
    documentation = ModelDocumentation.from_description(description)

    assert [table.name for table in documentation.spaces.table] == ["space_1", "space_2"]
    assert len(documentation.constructions.table) == 3
    assert documentation.systems.table[0].name == "boiler"
    assert all(layer.thickness > 0 for table in documentation.constructions.table for layer in table.layers)
    assert documentation.spaces.topic == "Spaces"


def test_the_html_report_has_the_tables_and_the_figures_of_the_results(description: ModelDescription) -> None:
    content = ContentModelDocumentation(
        title="Two rooms",
        spaces=ContentDocumentation(title="The spaces", introduction="Two rooms with a storage tank."),
        constructions=ContentDocumentation(),
        systems=ContentDocumentation(conclusions="One boiler."),
    )

    without = to_html_reporting(ModelDocumentation.from_description(description, content))
    html = to_html_reporting(ModelDocumentation.from_description(description, content, ResultFile(path=RESULT)))

    assert "<title>Two rooms</title>" in html
    assert "The spaces" in html and "Two rooms with a storage tank." in html and "One boiler." in html
    assert "space_1" in html and "boiler" in html
    assert "plotly-graph-div" not in without
    assert html.count("plotly-graph-div") >= 3  # one figure per kind of space figure, both spaces on it


def test_a_report_is_made_from_the_two_files(tmp_path: Path) -> None:
    from_files = ModelDocumentation.from_files(DESCRIPTION, RESULT)

    assert from_files.result == ResultFile(path=RESULT)
    assert from_files.description == ModelDescription.read(DESCRIPTION)
    assert "plotly-graph-div" in to_html_reporting(from_files)


def test_the_word_report_has_a_table_per_element_and_figures_with_results(tmp_path: Path) -> None:
    without = to_docx(ModelDocumentation.from_files(DESCRIPTION), tmp_path / "without.docx")
    with_results = to_docx(ModelDocumentation.from_files(DESCRIPTION, RESULT), tmp_path / "with.docx")

    assert len(without.tables) == 6
    assert len(without.inline_shapes) == 0
    assert len(with_results.tables) == 6
    assert len(with_results.inline_shapes) == 13
    assert (tmp_path / "with.docx").exists()


def test_the_figures_of_an_element_are_plotted_from_the_results(description: ModelDescription) -> None:
    data = Reader(str(RESULT), "openmodelica")
    figures = description.figures["space_1"]

    assert len(plot_figures(data, figures)) == len(figures)
    assert len(plot_figures(data, figures, plot_plot_ly)) == len(figures)
    assert plot_plot_ly_many(data, list(description.space_figures["space_1"][:1])) is not None
    documentation = ModelDocumentation.from_files(DESCRIPTION, RESULT)
    assert len(get_figures("space_1", documentation)) == len(figures)
    assert get_figures("unknown", documentation) == []


def test_a_figure_of_variables_missing_from_the_results_is_left_out(description: ModelDescription) -> None:
    data = Reader(str(RESULT), "openmodelica")
    missing = NamedFigure.model_validate(
        {"name": "missing", "left_axis": {"label": "T [K]", "lines": [{"key": "nowhere.T", "label": "T [K]"}]}}
    )

    assert plot_plot_ly(data, missing) is None
    assert plot_figures(data, [missing], plot_plot_ly) == []
    assert plot(data, missing) is not None  # matplotlib draws the empty axes


def test_temperatures_are_plotted_in_celsius(description: ModelDescription) -> None:
    data = Reader(str(RESULT), "openmodelica")
    figure = description.figures["space_1"][0]

    plotly_figure = plot_plot_ly(data, figure)

    assert plotly_figure is not None
    temperature = next(trace for trace in plotly_figure.data if "[degC]" in trace.name)
    assert 0 < max(temperature.y) < 60
    assert plotly_figure.layout.xaxis.title.text == "Time [days]"
