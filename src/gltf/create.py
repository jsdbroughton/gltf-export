import json
from typing import cast, Dict, Any

import numpy as np
from pygltflib import (
    GLTF2,
    Scene,
    Mesh,
    Node,
    Primitive,
    Attributes,
    Buffer,
    BufferView,
    Accessor,
)
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh as SpeckleMesh

from src.gltf.mesh import process_speckle_mesh, is_speckle_mesh
from src.utils.flatten import flatten_base


def create_gltf(speckle_data: Base, include_metadata: bool):
    gltf = GLTF2()

    scene = Scene(nodes=[])
    gltf.scenes.append(scene)
    gltf.scene = 0  # Set the default scene

    for obj in flatten_base(speckle_data):
        display_value: Base = getattr(obj, "displayValue", None)

        if isinstance(display_value, list):
            display_meshes = display_value
        else:
            display_meshes = [display_value]

        for display in display_meshes:
            if is_speckle_mesh(display):
                display_mesh = cast(SpeckleMesh, display)

                vertices, faces = process_speckle_mesh(display_mesh)

                mesh = Mesh(primitives=[create_primitive(vertices, faces, gltf)])
                mesh_index = len(gltf.meshes)
                gltf.meshes.append(mesh)

                node = Node(mesh=mesh_index)
                node_index = len(gltf.nodes)
                gltf.nodes.append(node)

                scene.nodes.append(node_index)

                if include_metadata:
                    add_metadata_to_node(node, obj)

    return gltf


def create_primitive(vertices, faces, gltf):
    primitive = Primitive(
        attributes=Attributes(POSITION=len(gltf.accessors)),
        indices=len(gltf.accessors) + 1,
    )

    vertices_array = vertices.flatten()

    # Create a buffer and append it to the GLTF object
    vertices_buffer = Buffer()
    vertices_buffer.uri = None  # Typically, you'd set this if you want an external file
    gltf.buffers.append(vertices_buffer)

    vertices_buffer_view = BufferView(
        buffer=len(gltf.buffers) - 1,
        byteOffset=0,
        byteLength=len(vertices_array.tobytes()),
        target=34962,  # GL_ARRAY_BUFFER
    )
    gltf.bufferViews.append(vertices_buffer_view)

    vertices_accessor = Accessor(
        bufferView=len(gltf.bufferViews) - 1,
        componentType=5126,  # GL_FLOAT
        count=len(vertices),
        type="VEC3",
        max=vertices.max(axis=0).tolist(),
        min=vertices.min(axis=0).tolist(),
    )
    gltf.accessors.append(vertices_accessor)

    indices_array = faces.flatten().astype(np.uint32)

    # Create another buffer for indices
    indices_buffer = Buffer()
    gltf.buffers.append(indices_buffer)

    indices_buffer_view = BufferView(
        buffer=len(gltf.buffers) - 1,
        byteOffset=0,
        byteLength=len(indices_array.tobytes()),
        target=34963,  # GL_ELEMENT_ARRAY_BUFFER
    )
    gltf.bufferViews.append(indices_buffer_view)

    indices_accessor = Accessor(
        bufferView=len(gltf.bufferViews) - 1,
        componentType=5125,  # GL_UNSIGNED_INT
        count=len(indices_array),
        type="SCALAR",
        max=[indices_array.max()],
        min=[indices_array.min()],
    )
    gltf.accessors.append(indices_accessor)

    # Adding data to buffers after they have been initialized
    gltf.buffers[-2].data = vertices_array.tobytes()
    gltf.buffers[-1].data = indices_array.tobytes()

    return primitive


def add_metadata_to_node(node: Node, obj: Base):
    metadata = extract_metadata(obj)
    if metadata:
        if node.extras is None:
            node.extras = {}
        node.extras["speckle_metadata"] = metadata


def extract_metadata(obj: Base) -> Dict[str, Any]:
    metadata = {}
    for attr, value in obj.__dict__.items():
        if not attr.startswith("_") and attr not in ["vertices", "faces", "colors"]:
            if isinstance(value, (str, int, float, bool)):
                metadata[attr] = value
            elif isinstance(value, (list, dict)):
                try:
                    # Attempt to JSON serialize complex structures
                    json.dumps(value)
                    metadata[attr] = value
                except TypeError:
                    # If it can't be JSON serialized, convert to string
                    metadata[attr] = str(value)
            else:
                # For other types, convert to string
                metadata[attr] = str(value)
    return metadata
