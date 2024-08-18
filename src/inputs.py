import json
from enum import Enum
from pathlib import Path
from typing import Optional, TypeVar

from pydantic import Field
from speckle_automate import AutomateBase
from speckle_automate.runner import AutomateGenerateJsonSchema


class ExportFormat(Enum):
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


def test_generate_schema():
    input_schema = FunctionInputs

    path = Path("schema.json")
    schema = json.dumps(
        input_schema.model_json_schema(
            by_alias=True, schema_generator=AutomateGenerateJsonSchema
        )
        if input_schema
        else {}
    )
    path.write_text(schema)
