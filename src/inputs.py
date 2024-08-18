import json
from enum import Enum
from pathlib import Path
from typing import Optional, TypeVar

from pydantic import Field
from pydantic.json_schema import GenerateJsonSchema
from speckle_automate import AutomateBase
from speckle_automate.runner import (
    AutomateGenerateJsonSchema as SDKAutomateGenerateJsonSchema,
)


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
    random_text: str = Field(
        title="required text test",
        description="this field is only here to test the required field flag",
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


class AutomateGenerateJsonSchema(GenerateJsonSchema):
    def __init__(self, by_alias: bool = True, ref_template: str = "#/$defs/{model}"):
        super().__init__(by_alias=by_alias, ref_template=ref_template)
        self.schema_dialect = "https://json-schema.org/draft/2020-12/schema"

    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)

        json_schema["$schema"] = self.schema_dialect

        if "properties" in json_schema:
            for prop, details in json_schema["properties"].items():
                self._process_property(
                    details, json_schema.get("$defs", {}), getattr(schema, prop, None)
                )

        if "$defs" in json_schema:
            defs = json_schema.pop("$defs")
            json_schema["$defs"] = defs

        return json_schema

    def _process_property(self, property_schema, defs, field):
        if "allOf" in property_schema and len(property_schema["allOf"]) == 1:
            ref = property_schema["allOf"][0].get("$ref")
            if ref and ref.startswith("#/$defs/"):
                enum_name = ref.split("/")[-1]
                if enum_name in defs:
                    enum_schema = defs[enum_name]
                    property_schema.update(enum_schema)
                    del property_schema["allOf"]

        if isinstance(field, Enum):
            property_schema["enum"] = [e.value for e in field.__class__]
            if "default" in property_schema:
                property_schema["default"] = property_schema["default"].value

        if "type" not in property_schema:
            if "enum" in property_schema:
                property_schema["type"] = "string"
            elif "default" in property_schema:
                property_schema["type"] = self._infer_type(property_schema["default"])
            else:
                property_schema["type"] = "object"

    def _infer_type(self, value):
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        else:
            return "object"
