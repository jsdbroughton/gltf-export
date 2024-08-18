from typing import List, Optional

import numpy as np
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh as SpeckleMesh, Vector
from specklepy.objects.other import Transform

from src.gltf.helpers import triangulate_face
from src.gltf.instances import apply_transformations, safe_apply_transformations


def is_speckle_mesh(obj: Base) -> bool:
    """
    Check if the object is a SpeckleMesh.
    This function checks for the presence of 'speckle_type' attribute
    and verifies if it's set to 'Objects.Geometry.Mesh'.
    """
    return (
        hasattr(obj, "speckle_type")
        and obj.speckle_type == "Objects.Geometry.Mesh"
        and hasattr(obj, "vertices")
        and hasattr(obj, "faces")
    )


def process_speckle_mesh(
    speckle_mesh: SpeckleMesh, transforms: Optional[List[Transform]] = None
) -> tuple:
    vertices = np.array(speckle_mesh.vertices, dtype=np.float32).reshape((-1, 3))

    # Apply any transformations if they exist
    # if transforms:
    #     vertices = safe_apply_transformations(vertices, transforms)

    # Perform Y/Z swap and negate new Y (old Z)
    vertices_swapped = vertices[:, [0, 2, 1]]  # Reorder columns to X, Z, Y
    vertices_swapped[:, 2] *= -1  # Negate the new Z (old Y)

    faces = []
    i = 0
    while i < len(speckle_mesh.faces):

        face_vertex_count = (
            speckle_mesh.faces[i] or 3
        )  # old displayMeshes used 0 to indicate a triangle, because of course they did

        i += 1  # Skip the vertex count
        face_vertex_indices = speckle_mesh.faces[i : i + face_vertex_count]
        face_vertices = [
            Vector.from_list(vertices_swapped[idx].tolist())
            for idx in face_vertex_indices
        ]
        if face_vertex_count == 3:
            faces.append(face_vertex_indices)
        else:
            triangulated = triangulate_face(face_vertices)
            faces.extend(
                [[face_vertex_indices[idx] for idx in tri] for tri in triangulated]
            )
        i += face_vertex_count

    # Convert faces to a numpy array with uint32 dtype
    faces = np.array(faces, dtype=np.uint32)

    return vertices_swapped, faces
