from pygltflib import Primitive, Attributes, BufferView, Accessor


def create_primitive(vertices, faces, gltf, buffer_data, material_index=None):
    primitive = Primitive(attributes=Attributes(POSITION=len(gltf.accessors)))

    if material_index is not None:
        primitive.material = material_index

    # Vertices
    vertices_byte_offset = len(buffer_data)
    vertices_byte_length = vertices.nbytes
    buffer_data.extend(vertices.tobytes())

    vertices_buffer_view = BufferView(
        buffer=0,
        byteOffset=vertices_byte_offset,
        byteLength=vertices_byte_length,
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

    # Indices
    indices_byte_offset = len(buffer_data)
    indices_byte_length = faces.nbytes
    buffer_data.extend(faces.tobytes())

    indices_buffer_view = BufferView(
        buffer=0,
        byteOffset=indices_byte_offset,
        byteLength=indices_byte_length,
        target=34963,  # GL_ELEMENT_ARRAY_BUFFER
    )
    gltf.bufferViews.append(indices_buffer_view)

    indices_accessor = Accessor(
        bufferView=len(gltf.bufferViews) - 1,
        componentType=5125,  # GL_UNSIGNED_INT
        count=faces.size,
        type="SCALAR",
        max=[int(faces.max())],
        min=[int(faces.min())],
    )
    gltf.accessors.append(indices_accessor)

    primitive.indices = len(gltf.accessors) - 1

    return primitive
