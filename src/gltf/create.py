import base64
from typing import cast, Optional

import trimesh
from pygltflib import (
    GLTF2,
    Scene,
    Mesh,
    Buffer,
    Asset,
)
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh as SpeckleMesh
from specklepy.objects.other import Transform
from trimesh.exchange.export import export_scene

from src.gltf.element import speckle_to_element
from src.gltf.helpers import add_nodes_and_meshes
from src.gltf.material import speckle_to_gltf_pbr
from src.gltf.mesh import process_speckle_mesh, is_speckle_mesh
from src.gltf.metadata import add_metadata_to_node
from src.gltf.primitive import create_primitive
from src.inputs import FunctionInputs, ExportFormat
from src.utils.checks import ElementCheckRules
from src.utils.flatten import (
    flatten_base_thorough,
    extract_base_and_transform,
)
from src.utils.store import prep_temp_file


def create_gltf(speckle_data: Base, include_metadata: bool):
    gltf = GLTF2()
    gltf.asset = Asset(version="2.0", generator="Speckle to GLTF Converter")
    main_scene = Scene(nodes=[])
    gltf.scenes.append(main_scene)
    gltf.scene = 0
    buffer = Buffer()
    gltf.buffers.append(buffer)
    buffer_data = bytearray()

    flattened = list(flatten_base_thorough(speckle_data))

    for obj_index, obj in enumerate(flattened):

        display_value: Base = getattr(obj, "displayValue", None) or getattr(
            obj, "@displayValue", None
        )  # old conversions may have used the @displayValue

        if isinstance(display_value, list):
            display_meshes = display_value
        else: 
            display_meshes = [display_value]

        mesh_indices = []
        for display in display_meshes:
            if is_speckle_mesh(display):
                display_mesh = cast(SpeckleMesh, display)
                vertices, faces = process_speckle_mesh(display_mesh)

                # Create material (if available)
                material_index = (
                    speckle_to_gltf_pbr(display_mesh.renderMaterial, gltf)
                    if hasattr(display_mesh, "renderMaterial")
                    else None
                )

                primitive = create_primitive(
                    vertices, faces, gltf, buffer_data, material_index
                )
                mesh = Mesh(primitives=[primitive])
                mesh_index = len(gltf.meshes)
                gltf.meshes.append(mesh)
                mesh_indices.append(mesh_index)

        if mesh_indices:
            node = add_nodes_and_meshes(gltf, main_scene, mesh_indices)

            if include_metadata:
                add_metadata_to_node(node, obj)

    buffer.uri = f"data:application/octet-stream;base64,{base64.b64encode(buffer_data).decode('ascii')}"
    buffer.byteLength = len(buffer_data)
    return gltf


def create_gltf_from_instances(speckle_data: Base, include_metadata: bool):
    gltf = GLTF2()
    gltf.asset = Asset(version="2.0", generator="Speckle to GLTF Converter")
    main_scene = Scene(nodes=[])
    gltf.scenes.append(main_scene)
    gltf.scene = 0
    buffer = Buffer()
    gltf.buffers.append(buffer)
    buffer_data = bytearray()

    for base, obj_id, transforms in extract_base_and_transform(speckle_data):
        display_value: Base = getattr(base, "displayValue", None)
        display_meshes = (
            display_value if isinstance(display_value, list) else [display_value]
        )

        mesh_indices = []
        for display in display_meshes:
            if is_speckle_mesh(display):
                display_mesh = cast(SpeckleMesh, display)
                vertices, faces = process_speckle_mesh(display_mesh, transforms)

                # Create material (if available)
                material_index = (
                    speckle_to_gltf_pbr(display_mesh.renderMaterial, gltf)
                    if hasattr(display_mesh, "renderMaterial")
                    else None
                )

                primitive = create_primitive(
                    vertices, faces, gltf, buffer_data, material_index
                )
                mesh = Mesh(primitives=[primitive])
                mesh_index = len(gltf.meshes)
                gltf.meshes.append(mesh)
                mesh_indices.append(mesh_index)

        if mesh_indices:
            node = add_nodes_and_meshes(gltf, main_scene, mesh_indices)

            if include_metadata:
                add_metadata_to_node(node, base)

    buffer.uri = f"data:application/octet-stream;base64,{base64.b64encode(buffer_data).decode('ascii')}"
    buffer.byteLength = len(buffer_data)
    return gltf


def create_gltf_from_trimesh(
    speckle_data: Base, model_name: str, function_inputs: FunctionInputs
):

    reference_objects: tuple[
        Base,
        str,
        Optional[Transform],
    ] = extract_base_and_transform(speckle_data)

    element_rules = ElementCheckRules()

    visible_objects_rule = element_rules.rule_combiner(
        element_rules.is_displayable_rule(),
    )

    reference_displayable_objects = [
        (base_obj, speckle_id, transform)
        for base_obj, speckle_id, transform in reference_objects
        if visible_objects_rule(base_obj)
    ]

    reference_elements = [
        speckle_to_element(obj) for obj in reference_displayable_objects
    ]

    if not reference_elements:
        return None

    # Create a Trimesh scene
    scene = trimesh.Scene()

    for element in reference_elements:
        for mesh in element.meshes:
            # Add each mesh to the scene
            scene.add_geometry(
                mesh,
                node_name=element.id,  # Use the element's ID as the node name
                metadata=(
                    {"speckle_id": element.id}
                    if function_inputs.include_metadata
                    else None
                ),
            )

    temp_file = prep_temp_file(model_name, ".glb")

    # Export the scene
    export_scene(scene, file_obj=temp_file, file_type="glb")

    return str(temp_file)
