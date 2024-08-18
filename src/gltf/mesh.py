from typing import List, Optional

import numpy as np
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh as SpeckleMesh, Vector
from specklepy.objects.other import Transform

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
        face_vertex_count = speckle_mesh.faces[i]
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


def area(a, b, c):
    return 0.5 * abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))


def is_ear(a, b, c, polygon):
    for p in polygon:
        if p not in [a, b, c] and area(a, b, p) + area(b, c, p) + area(c, a, p) == area(
            a, b, c
        ):
            return False
    return True


def triangulate_face(vertices: List[Vector]) -> List[List[int]]:
    """Triangulate a face with more than 3 vertices using ear clipping."""
    if len(vertices) == 3:
        return [[0, 1, 2]]

    polygon = list(range(len(vertices)))
    triangles = []

    while len(polygon) > 3:
        n = len(polygon)
        for i in range(n):
            prev = polygon[(i - 1) % n]
            current = polygon[i]
            next = polygon[(i + 1) % n]
            if is_ear(
                vertices[prev],
                vertices[current],
                vertices[next],
                [vertices[p] for p in polygon],
            ):
                triangles.append([prev, current, next])
                polygon.pop(i)
                break

    triangles.append(polygon)
    return triangles
