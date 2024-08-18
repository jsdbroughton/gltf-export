from typing import List, Optional

from pygltflib import GLTF2, Material, PbrMetallicRoughness


def extract_color(color_value):
    """Extract RGBA values from an integer color value."""
    if isinstance(color_value, int):
        if color_value == -1:  # Special case for white
            return [1.0, 1.0, 1.0, 1.0]
        a = (color_value >> 24) & 0xFF
        r = (color_value >> 16) & 0xFF
        g = (color_value >> 8) & 0xFF
        b = color_value & 0xFF
        return [r / 255, g / 255, b / 255, 1 - (a / 255)]  # Convert alpha to opacity
    return [1.0, 1.0, 1.0, 1.0]  # Default white color if conversion fails


def create_material(gltf: GLTF2, color: List[float]) -> int:
    material = Material(
        pbrMetallicRoughness=PbrMetallicRoughness(
            baseColorFactor=color, metallicFactor=0.0, roughnessFactor=0.5
        )
    )
    material_index = len(gltf.materials)
    gltf.materials.append(material)
    return material_index


def speckle_to_gltf_pbr(material, gltf: GLTF2) -> Optional[int]:
    if material is None:
        return None

    base_color = extract_color(getattr(material, "diffuse", -1))
    opacity = getattr(material, "opacity", 1.0)
    base_color[3] = opacity  # Set alpha channel

    gltf_material = Material(
        pbrMetallicRoughness={
            "baseColorFactor": extract_color(getattr(material, "diffuse", -1)),
            "metallicFactor": getattr(material, "metalness", 0.0),
            "roughnessFactor": getattr(material, "roughness", 1.0),
        },
        name=getattr(material, "name", "Unnamed Material"),
    )

    if opacity < 1.0:
        gltf_material.alphaMode = "BLEND"
    else:
        gltf_material.alphaMode = "OPAQUE"

    # Only set alphaCutoff if alphaMode is "MASK"
    if getattr(material, "alpha_mode", "").upper() == "MASK":
        gltf_material.alphaMode = "MASK"
        gltf_material.alphaCutoff = getattr(material, "alpha_cutoff", 0.5)

    # Ensure alphaCutoff is not included for non-MASK modes
    if gltf_material.alphaMode != "MASK":
        gltf_material.alphaCutoff = None

    emissive = getattr(material, "emissive", None)
    if emissive is not None and emissive != -16777216:  # If not black
        gltf_material.emissiveFactor = extract_color(emissive)[
            :3
        ]  # Only use RGB values

    # Check if this material already exists in the materials array
    for i, existing_material in enumerate(gltf.materials):
        if existing_material == gltf_material:
            return i  # Return the index of the existing material

    # If the material doesn't exist, add it to the array and return its index
    gltf.materials.append(gltf_material)
    return len(gltf.materials) - 1
