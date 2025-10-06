import json
from prefect import Parameter
from prefect.tasks.dbt import DbtShellTask
from prefect.tasks.shell import ShellTask


def run_flow_and_return_output(flow, **kwargs):
    """
    Prefect flow run returns prefect.engine.state (Success/Failed) object and it has 
    flow attributes (name, status, tasks). The status of each task is stored in the 
    result object, which is dictionary type of {TaskObject: TaskResultObject}
    """

    command = None
    
    for key, value in kwargs.items():
        if key == "command":
            command = value
    if command is not None:
        state = flow.run(command=command)
    else :
        state = flow.run()
    

    tasks = []
    for task_item, status_item in state.result.items():
        if not isinstance(task_item, Parameter):

            task_meta = {}
            task_output = []

            if isinstance(task_item, DbtShellTask) or isinstance(task_item, ShellTask):
                task_meta = {"command": command if command is not None else task_item.command}
                try:
                    task_output = [json.loads(output) for output in status_item.result]
                except:
                    try:
                        task_output.append({"message": "\n".join(status_item.result)})
                    except:
                        pass
            else:
                task_output = str(status_item.result)

            tasks.append(
                {"task_name": task_item.name,
                "task_type": task_item.serialize()["type"],
                "is_successful": status_item.is_successful(),
                "message": status_item.message,
                "task_meta": task_meta,
                "task_output": task_output
                })

    response = {
        "flow_name": flow.name,
        "is_successful": state.is_successful(),
        "tasks": tasks
    }

    return response
 