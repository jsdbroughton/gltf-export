from typing import List

import numpy as np
from specklepy.objects.other import Transform as SpeckleTransform


def transform_list_to_matrix(transform_list: List[float]) -> np.ndarray:
    """
    Converts a flat list of 16 floats into a 4x4 matrix.

    Parameters:
    - transform_list (List[float]): A flat list of 16 floats representing the transformation matrix.

    Returns:
    - np.ndarray: A 4x4 NumPy matrix.
    """
    if len(transform_list) != 16:
        raise ValueError("Transform list must contain exactly 16 elements.")
    return np.array(transform_list).reshape(4, 4)


def combine_transform_matrices(transforms: List[SpeckleTransform]) -> np.ndarray:
    """
    Combine multiple transformation matrices into a single matrix.

    Args:
        transforms (List[SpeckleTransform]): A list of Speckle Transform objects.

    Returns:
        np.ndarray: A combined 4x4 transformation matrix.
    """
    combined_matrix = np.identity(4)
    for transform in transforms:
        matrix = convert_speckle_transform_to_matrix(transform)
        combined_matrix = np.dot(combined_matrix, matrix)
    return combined_matrix


def convert_speckle_transform_to_matrix(transform: SpeckleTransform) -> np.ndarray:
    """
    Convert a Speckle Transform object to a 4x4 NumPy matrix.

    Args:
        transform (SpeckleTransform): The Speckle Transform object.

    Returns:
        np.ndarray: A 4x4 transformation matrix.
    """
    return np.array(transform.matrix).reshape(4, 4)


def apply_transformations(
    vertices: np.ndarray, transforms: List[SpeckleTransform]
) -> np.ndarray:
    """
    Apply a series of transformations to a set of vertices.
    Args:
        vertices (np.ndarray): The vertex positions to transform.
        transforms (List[SpeckleTransform]): A list of Speckle Transform objects to apply.
    Returns:
        np.ndarray: Transformed vertex positions.
    """
    # Convert to homogeneous coordinates
    vertices_homogeneous = np.hstack([vertices, np.ones((vertices.shape[0], 1))])

    # Combine all transformations into a single matrix
    final_transform = combine_transform_matrices(transforms)

    # Apply the combined transformation
    transformed_vertices = np.dot(vertices_homogeneous, final_transform.T)

    # Convert back to 3D coordinates (divide by w)
    transformed_vertices = transformed_vertices[:, :3] / transformed_vertices[:, 3:]

    return transformed_vertices


def safe_apply_transformations(
    vertices: np.ndarray, transforms: List[SpeckleTransform]
) -> np.ndarray:
    """
    Safely apply transformations with error checking and handling.
    """
    try:
        transformed = apply_transformations(vertices, transforms)

        # Check for invalid values
        if np.any(np.isinf(transformed)) or np.any(np.isnan(transformed)):
            print("Warning: Invalid values detected after transformation")
            # Replace inf and nan with large finite values
            transformed = np.nan_to_num(transformed, nan=0.0, posinf=1e30, neginf=-1e30)

        # Check for extreme values
        max_abs_val = np.max(np.abs(transformed))
        if max_abs_val > 1e10:  # Adjust this threshold as needed
            print(
                f"Warning: Extreme values detected. Max absolute value: {max_abs_val}"
            )
            # Normalize the vertices
            transformed = (
                transformed / max_abs_val * 1e5
            )  # Scale to a more reasonable range

        return transformed

    except Exception as e:
        print(f"Error during transformation: {str(e)}")
        # Return original vertices if transformation fails
        return vertices
