import base64
import tempfile
from datetime import datetime
from pathlib import Path
import io
from typing import IO

import httpx
from pygltflib import GLTF2

from speckle_automate import AutomationContext

from src.inputs import ExportFormat


def prep_temp_file(model_name: str, file_extension: str) -> Path:
    temp_file = Path(
        tempfile.gettempdir(),
        f"{model_name}_{datetime.now().timestamp():.0f}{file_extension}",
    )
    temp_file.parent.mkdir(parents=True, exist_ok=True)

    return temp_file


def write_gltf_to_tmp(
    gltf_content: GLTF2, model_name: str, export_format: ExportFormat
) -> str:
    if export_format == ExportFormat.GLB:
        temp_file = prep_temp_file(model_name, ".glb")
        gltf_content.save_binary(temp_file)

    else:  # GLTF
        temp_file = prep_temp_file(model_name, ".gltf")
        gltf_content.save(temp_file)

    return str(temp_file)


def safe_store_file_result(automate_context: AutomationContext, file_name: str):
    # Store the original URL
    original_url = automate_context.automation_run_data.speckle_server_url

    try:
        # Modify the URL property of the automation_run_data
        automate_context.automation_run_data.speckle_server_url = original_url.rstrip(
            "/"
        )

        # Attempt to store the file
        automate_context.store_file_result(file_name)
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise

        else:
            # Handle the 404 error
            error_message = f"Unable to store file: {file_name}. Error: {str(e)}"
            print(error_message)  # For logging purposes
            # automate_context.mark_run_exception(error_message)
    finally:
        # Restore the original URL
        automate_context.automation_run_data.speckle_server_url = original_url
