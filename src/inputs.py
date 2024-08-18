from enum import Enum
from pydantic import Field
from speckle_automate import AutomateBase


class ExportFormat(str, Enum):
    GLTF = "gltf"
    GLB = "glb"


class FunctionInputs(AutomateBase):
    """Input parameters for the GLTF/GLB exporter function."""

    export_format: ExportFormat = Field(
        default=ExportFormat.GLTF,
        title="Export Format",
        description="The format of the exported file: 'gltf' or 'glb'",
    )
    include_metadata: bool = Field(
        default=False,
        title="Include Metadata",
        description="Whether to include Speckle metadata in the export",
    )
