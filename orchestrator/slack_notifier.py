import os
from io import TextIOWrapper

import re
import json
import logging
import textwrap
from tabulate import tabulate
from slack_sdk import WebClient
from prefect.core.flow import Flow


def wrap(text: str, width: int) -> str:
    return "" if text is None else "\n".join(textwrap.wrap(text=text, width=width))


def create_and_open(file_path: str) -> TextIOWrapper:
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return open(file_path, "w")


def flow_info_slack(flow: Flow) -> str:
    tasks_info = tabulate(
        tabular_data=[
            {
                "task_name": wrap(task.name, 50),
                "task_type": re.search(r"(?<=\.)(\w+)(?=')", str(type(task))).group(1), # type: ignore
                "task_info": wrap(task.command if hasattr(task, "command") else "", 90) # type: ignore
            }
            for task in flow.tasks
        ], 
        headers="keys", 
        tablefmt="grid"
    )
    slack_message = f"*`{flow.name}`* started and includes below tasks:\n```{tasks_info}```"
    return slack_message


def flow_output_slack(response: dict) -> str:
    message_text = tabulate(
        tabular_data=[
            {
                "task_name": wrap(task.get("task_name", ""), 50),
                "is_successful": task.get("is_successful", ""), 
                "message": wrap(task.get("message", ""), 90)
            }
            for task in response.get("tasks", [])
            ],
        headers="keys",
        tablefmt="grid"
    )
    return message_text


def notify_pipeline_start(
    flow: Flow, 
    token: str,
    channel_id: str
    ) -> None:
    message_text = flow_info_slack(flow)
    client = WebClient(token=token)
    try:    
        message = client.chat_postMessage(
            channel=channel_id,
            link_names=True,
            text=message_text
        )
        logging.info({"message": f"The slack notification was sent successfully on channel {message.get('channel')}"})
    except Exception as e:
        logging.error({"message": f"Something happened while trying to send slack notification: {str(e)}"})


def notify_pipeline_end(
    response: dict,
    token: str,
    channel_id: str
    ) -> None:
    upload_files = []
    flow_output_file = "__flow_output__/flow_output.json"
    message_title = f"""*`{response.get("flow_name")}`* {"is finished successfully :tada:" if response.get("is_successful") else "failed :cry: @here "}"""
    message_text = flow_output_slack(response=response)

    try: 
        for task in response.get("tasks", []):
            if task.get("task_type") == "prefect.tasks.dbt.dbt.DbtShellTask":
                task_output = re.sub(pattern=r"\x1b\[\d*m", repl="", string=task["task_output"][0]["message"]) # curate special characters
                print(task_output)
                dbt_output_file = f"__flow_output__/dbt_output_{task.get('task_name', '')}.txt"
                with create_and_open(dbt_output_file) as f:
                    f.write(task_output)
                    f.close()
                upload_files.append(dbt_output_file)
                
            elif task.get("task_type") == "prefect.tasks.great_expectations.checkpoints.RunGreatExpectationsValidation":
                ge_output_file = f"__flow_output__/ge_output_{task.get('task_name', '')}.json"
                json.dump(task["task_output"][0]["run_results"], create_and_open(ge_output_file), indent=4)
                upload_files.append(ge_output_file)
            
        if not response.get("is_successful"):
            json.dump(response, create_and_open(flow_output_file), indent=4)
            upload_files.append(flow_output_file)

        client = WebClient(token=token)

        for file in upload_files:
            upload = client.files_upload_v2(file=file, filename=file)
            message_text = message_text + "<" + upload["file"]["permalink"] + "| >" # type: ignore
        
        message = client.chat_postMessage(
            channel=channel_id,
            link_names=True,
            text=f"{message_title}```{message_text}```"
        )
        logging.info({"message": f"The slack notification was sent successfully on channel {message.get('channel')}"})

    except Exception as e:
        logging.error({"message": f"Something happened while trying to send slack notification: {str(e)}"})
