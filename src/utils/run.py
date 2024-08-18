from speckle_automate import AutomationContext


def get_modelname(automate_context: AutomationContext) -> str:
    version_id = automate_context.automation_run_data.triggers[0].payload.version_id
    project_id = automate_context.automation_run_data.project_id
    version = automate_context.speckle_client.commit.get(project_id, version_id)
    return getattr(version, "branchName", "model")
