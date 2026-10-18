"""What the reports need to know of a model, written next to it by the tool that generated it (trano).

The records of the spaces, the constructions and the systems are the data of the report tables; the figures name
the result variables to plot for each element; the parameter descriptions explain the table rows.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from trano_simulate.plot.figure import NamedFigure

DESCRIPTION_SUFFIX = ".description.json"


class ModelDescription(BaseModel):
    name: str = Field(default="", description="Name of the Modelica package")
    spaces: list[dict[str, Any]] = Field(default_factory=list, description="Records of the space tables")
    constructions: list[dict[str, Any]] = Field(default_factory=list, description="Records of the construction tables")
    systems: list[dict[str, Any]] = Field(default_factory=list, description="Records of the system tables")
    figures: dict[str, list[NamedFigure]] = Field(
        default_factory=dict, description="Figures of each element, with those of its subsystems, in plotting order"
    )
    space_figures: dict[str, list[NamedFigure]] = Field(
        default_factory=dict, description="Figures of each space, plotted side by side for all spaces"
    )
    parameter_descriptions: dict[str, str] = Field(default_factory=dict, description="Description of each parameter")

    def write(self, path: Path) -> Path:
        path.write_text(self.model_dump_json(indent=2))
        return path

    @classmethod
    def read(cls, path: Path) -> "ModelDescription":
        return cls.model_validate_json(path.read_text())
