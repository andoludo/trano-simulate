"""Reports of a simulated model, from its description file and its result file."""

from trano_simulate.reporting.description import DESCRIPTION_SUFFIX, ModelDescription
from trano_simulate.reporting.docx import to_docx
from trano_simulate.reporting.html import to_html_reporting
from trano_simulate.reporting.reporting import ContentModelDocumentation, ModelDocumentation
from trano_simulate.reporting.types import ContentDocumentation, ResultFile

__all__ = [
    "DESCRIPTION_SUFFIX",
    "ContentDocumentation",
    "ContentModelDocumentation",
    "ModelDescription",
    "ModelDocumentation",
    "ResultFile",
    "to_docx",
    "to_html_reporting",
]
