from enum import Enum
from pydantic import Field
from speckle_automate import AutomateBase


class ExportFormat(Enum):
    GLTF = "gltf"
    GLB = "glb"


def create_one_of_enum(enum_cls):
    """
    Helper function to create a JSON schema from an Enum class.
    This is used for generating user input forms in the UI.
    """
    return [{"const": item.value, "title": item.name} for item in enum_cls]


class FunctionInputs(AutomateBase):
    """Input parameters for the GLTF/GLB exporter function."""

    export_format: ExportFormat = Field(
        default=ExportFormat.GLTF,
        title="Export Format",
        description="The format of the exported file: 'gltf' or 'glb'",
        json_schema_extra={
            "oneOf": create_one_of_enum(ExportFormat),
        },
    )
    include_metadata: bool = Field(
        default=False,
        title="Include Metadata",
        description="Whether to include Speckle metadata in the export",
    )
