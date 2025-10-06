import logging
import subprocess
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Response, status

from flows.selector import flow_selector
from orchestrator.config import SLACK_CHANNEL_ID, SLACK_BOT_TOKEN
from orchestrator.runner import run_flow_and_return_output
from orchestrator.slack_notifier import notify_pipeline_start, notify_pipeline_end


class PrefectRequestSchema(BaseModel):
    flow_name: str
    slack_channel_id: Optional[str] = SLACK_CHANNEL_ID


class DBTRequestSchema(BaseModel):
    command: str
    slack_channel_id: Optional[str] = SLACK_CHANNEL_ID


class ResponseSchema(BaseModel):
    is_executed: bool
    output: dict


app = FastAPI(openapi_url="/openapi.json")


@app.post("/prefect")
def run_flow(request: PrefectRequestSchema, response: Response):
    channel_id = request.slack_channel_id
    try:
        flow_to_run = flow_selector(request.flow_name)
        if channel_id and SLACK_BOT_TOKEN:
            notify_pipeline_start(flow=flow_to_run, token=SLACK_BOT_TOKEN, channel_id=channel_id) # type: ignore
        output = run_flow_and_return_output(flow_to_run)
        if channel_id and SLACK_BOT_TOKEN:
            notify_pipeline_end(response=output, token=SLACK_BOT_TOKEN, channel_id=channel_id) # type: ignore
        response.status_code = status.HTTP_200_OK
        results = {"is_executed": True, "output": output}
        logging.info({"message": f"{request.flow_name} execution finished", **results})
        return ResponseSchema(**results)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        output = {"message": str(e)}
        results = {"is_executed": False, "output": output}
        logging.critical({"message": f"{request.flow_name} execution failed", **results})
        return ResponseSchema(**results)


@app.post("/dbt")
def run_dbt(request: DBTRequestSchema, response: Response):
    from flows.generic import flow_generic_dbt
    channel_id = request.slack_channel_id
    try:
        if channel_id and SLACK_BOT_TOKEN:
            notify_pipeline_start(flow=flow_generic_dbt, token=SLACK_BOT_TOKEN, channel_id=channel_id)
        output = run_flow_and_return_output(flow_generic_dbt, command=request.command)
        if channel_id and SLACK_BOT_TOKEN:
            notify_pipeline_end(response=output, token=SLACK_BOT_TOKEN, channel_id=channel_id)
        response.status_code = status.HTTP_200_OK
        return ResponseSchema(**{"is_executed": True, "output": output})
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        output = {"message": str(e)}
        return ResponseSchema(**{"is_executed": False, "output": output})


@app.get("/elementary")
def run_elementary(response: Response):
    try:
        slack_channel_name = SLACK_CHANNEL_ID if SLACK_CHANNEL_ID is not None else ""
        slack_bot_token = SLACK_BOT_TOKEN if SLACK_BOT_TOKEN is not None else ""
        result = subprocess.run([
            "edr", "send-report", "--gcs-bucket-name", "bdw-elementary-reports", "--bucket-file-path", "report.html",
            "--slack-channel-name", slack_channel_name,  "--slack-token", slack_bot_token, "--update-bucket-website", "true",
            "--env", "prod", "--project-name", "demo_project", "--days-back", "30"
            ],
            capture_output=True, 
            text=True,
            check=True
        )
        logging.info(result.stdout)
        response.status_code = status.HTTP_200_OK
        message = f"Elementary report created.\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        logging.error(e.stderr)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = f"Elementary report failed.\n{e.stderr}"
    return {"message": message}