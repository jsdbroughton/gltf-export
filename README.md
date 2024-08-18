# Speckle GLTF/GLB Exporter Function

This repository contains a Speckle Automate function that exports Speckle data to GLTF or GLB format. It's designed to
work with the Speckle Automate platform, allowing for automated conversion of Speckle models to formats commonly used in
3D visualization and game development.

## Function Overview

The function takes a Speckle model as input and converts it to either GLTF or GLB format. It can optionally include
Speckle metadata in the exported file.

### Input Parameters

The function accepts the following input parameters:

- `export_format`: The format of the exported file. Can be either 'gltf' or 'glb'.

    - Default: 'gltf'


- `include_metadata`: Whether to include Speckle metadata in the export.

    - Default: False

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.