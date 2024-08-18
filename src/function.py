from speckle_automate import AutomationContext
from specklepy.objects import Base

from src.gltf.create import (
    create_gltf,
    create_gltf_from_instances,
    create_gltf_from_trimesh,
)
from src.inputs import FunctionInputs
from src.utils.store import safe_store_file_result, write_gltf_to_tmp


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """
    This function exports the Speckle model to GLTF or GLB format.

    Args:
        automate_context: The automation context provided by Speckle Automate.
        function_inputs: An instance of FunctionInputs containing export parameters.
    """
    # Receive the version data
    version_root_object: Base = automate_context.receive_version()

    # Get the model name from the version
    model_name: str = getattr(version_root_object, "name", "exported_model")

    gltf_data = create_gltf(version_root_object, function_inputs.include_metadata)

    # gltf_data = create_gltf_from_instances(
    #     version_root_object, function_inputs.include_metadata
    # )

    # file_name = create_gltf_from_trimesh(
    #     version_root_object, model_name, function_inputs
    # )

    file_name: str = write_gltf_to_tmp(
        gltf_data, model_name, function_inputs.export_format
    )

    #
    # automate_context.store_file_result(file_name)
    safe_store_file_result(automate_context, file_name)

    # Mark the run as successful
    automate_context.mark_run_success(
        f"{function_inputs.export_format.value.upper()} export completed: {file_name}"
    )
