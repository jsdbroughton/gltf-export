import json
from typing import Dict, Any

import numpy as np
from pygltflib import Node
from specklepy.objects import Base


def add_metadata_to_node(node: Node, obj: Base):
    metadata = extract_metadata(obj)
    if metadata:
        if node.extras is None:
            node.extras = {}
        node.extras["speckle_metadata"] = metadata


def numpy_to_python(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: numpy_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_python(v) for v in obj]
    return obj


def extract_metadata(obj: Base) -> Dict[str, Any]:
    metadata = {}
    for attr, value in obj.__dict__.items():
        if not attr.startswith("_") and attr not in ["vertices", "faces", "colors"]:
            if isinstance(value, (str, int, float, bool)):
                metadata[attr] = value
            else:
                # Convert numpy types to Python native types
                converted_value = numpy_to_python(value)
                try:
                    # Attempt to JSON serialize
                    json.dumps(converted_value)
                    metadata[attr] = converted_value
                except TypeError:
                    # If it still can't be JSON serialized, convert to string
                    metadata[attr] = str(converted_value)
    return metadata
