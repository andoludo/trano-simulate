"""The documentation of a model: its spaces, constructions and systems, and the figures of its results."""

from pathlib import Path
from typing import Literal, Self

from pydantic import computed_field

from trano_simulate.reporting.description import ModelDescription
from trano_simulate.reporting.types import (
    BaseTable,
    ConstructionTable,
    ContentDocumentation,
    ResultFile,
    SpaceTable,
    SystemTable,
    Topic,
)


class BaseDocumentation(ContentDocumentation):
    title: str | None = None
    introduction: str | None = None
    table: BaseTable | list[BaseTable]
    conclusions: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def topic(self) -> Topic:
        return type(self).__name__.replace("Documentation", "")  # type: ignore[return-value]


class SpacesDocumentation(BaseDocumentation):
    table: list[SpaceTable]  # type: ignore[assignment]

    @classmethod
    def from_description(
        cls, description: ModelDescription, content_documentation: ContentDocumentation
    ) -> "SpacesDocumentation":
        return cls(
            table=[SpaceTable(**space) for space in description.spaces],
            **content_documentation.model_dump(exclude_none=True),
        )


class ConstructionDocumentation(BaseDocumentation):
    table: list[ConstructionTable]  # type: ignore[assignment]

    @classmethod
    def from_description(
        cls, description: ModelDescription, content_documentation: ContentDocumentation
    ) -> "ConstructionDocumentation":
        return cls(
            table=[ConstructionTable(**construction) for construction in description.constructions],
            **content_documentation.model_dump(exclude_none=True),
        )


class SystemsDocumentation(BaseDocumentation):
    table: list[SystemTable]  # type: ignore[assignment]

    @classmethod
    def from_description(
        cls, description: ModelDescription, content_documentation: ContentDocumentation
    ) -> "SystemsDocumentation":
        return cls(
            table=[SystemTable(**system) for system in description.systems],
            **content_documentation.model_dump(exclude_none=True),
        )


class ContentModelDocumentation(ContentDocumentation):
    spaces: ContentDocumentation
    constructions: ContentDocumentation
    systems: ContentDocumentation


def _empty_content() -> ContentModelDocumentation:
    return ContentModelDocumentation(
        spaces=ContentDocumentation(), constructions=ContentDocumentation(), systems=ContentDocumentation()
    )


class ModelDocumentation(ContentDocumentation):
    spaces: SpacesDocumentation
    constructions: ConstructionDocumentation
    systems: SystemsDocumentation
    description: ModelDescription
    result: ResultFile | None = None

    @classmethod
    def from_description(
        cls,
        description: ModelDescription,
        content_model_documentation: ContentModelDocumentation | None = None,
        result: ResultFile | None = None,
    ) -> Self:
        content = content_model_documentation or _empty_content()
        return cls(
            **content.model_dump(exclude_none=True, exclude={"spaces", "constructions", "systems"}),
            spaces=SpacesDocumentation.from_description(description, content.spaces),
            constructions=ConstructionDocumentation.from_description(description, content.constructions),
            systems=SystemsDocumentation.from_description(description, content.systems),
            description=description,
            result=result,
        )

    @classmethod
    def from_files(
        cls,
        description_path: Path,
        result_path: Path | None = None,
        content_model_documentation: ContentModelDocumentation | None = None,
        result_type: Literal["openmodelica", "dymola"] = "openmodelica",
    ) -> Self:
        """The documentation of a model from its description file and, for the figures, its result file."""
        result = ResultFile(path=result_path, type=result_type) if result_path is not None else None
        return cls.from_description(ModelDescription.read(description_path), content_model_documentation, result)
