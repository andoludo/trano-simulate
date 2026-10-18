"""The figures of a report: lines of result variables on a left and a right axis."""

from pydantic import BaseModel, ConfigDict, Field


class Line(BaseModel):
    """A result variable (``key``, matched at the end of the variable names of the result file) and its style."""

    model_config = ConfigDict(extra="ignore")

    key: str | None = None
    color: str = "grey"
    label: str
    line_style: str = "solid"
    line_width: float = 1.5


class Axis(BaseModel):
    lines: list[Line] = Field(default=[])
    label: str


class Figure(BaseModel):
    model_config = ConfigDict(extra="ignore")

    right_axis: Axis = Field(default=Axis(lines=[], label=""))
    left_axis: Axis = Field(default=Axis(lines=[], label=""))


class NamedFigure(Figure):
    name: str
