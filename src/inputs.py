import json
from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic.json_schema import GenerateJsonSchema
from speckle_automate import AutomateBase


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


def test_generate_schema(path_given="schema.json"):
    input_schema = FunctionInputs

    path = Path(path_given)
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
            for def_name, def_schema in json_schema["$defs"].items():
                self._process_property(def_schema, json_schema["$defs"], None)

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

        if "enum" in property_schema:
            enum_values = property_schema["enum"]
            property_schema["oneOf"] = [
                {"const": value, "title": str(value).upper()} for value in enum_values
            ]
            del property_schema["enum"]

        if isinstance(field, Enum):
            property_schema["oneOf"] = [
                {"const": item.value, "title": item.name} for item in field.__class__
            ]
            if "default" in property_schema:
                property_schema["default"] = property_schema["default"].value

        if "type" not in property_schema:
            if "oneOf" in property_schema:
                property_schema["type"] = "string"
            elif "default" in property_schema:
                property_schema["type"] = self._infer_type(property_schema["default"])
            else:
                property_schema["type"] = "object"

    @staticmethod
    def _infer_type(value):
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
