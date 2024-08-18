from speckle_automate import AutomationContext
from specklepy.objects import Base

from src.gltf.create import create_gltf
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

    file_name: str = write_gltf_to_tmp(
        gltf_data, model_name, FunctionInputs.export_format
    )
    safe_store_file_result(automate_context, file_name)

    # Mark the run as successful
    automate_context.mark_run_success(
        f"{function_inputs.export_format.value.upper()} export completed: {file_name}"
    )
