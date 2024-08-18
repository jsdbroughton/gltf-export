from typing import List

import numpy as np
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh as SpeckleMesh, Vector


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


def process_speckle_mesh(speckle_mesh: SpeckleMesh) -> object:
    vertices = np.array(speckle_mesh.vertices).reshape((-1, 3))
    faces = []
    i = 0
    while i < len(speckle_mesh.faces):
        face_vertex_count = speckle_mesh.faces[i]
        i += 1  # Skip the vertex count
        face_vertex_indices = speckle_mesh.faces[i : i + face_vertex_count]
        face_vertices = [
            Vector.from_list(vertices[idx].tolist()) for idx in face_vertex_indices
        ]
        if face_vertex_count == 3:
            faces.append(face_vertex_indices)
        else:
            triangulated = triangulate_face(face_vertices)
            faces.extend(
                [[face_vertex_indices[idx] for idx in tri] for tri in triangulated]
            )
        i += face_vertex_count
    return vertices, np.array(faces)


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
