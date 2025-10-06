from prefect import Flow
from prefect.tasks.dbt import DbtShellTask
from  orchestrator.config import DBT_PROFILES_DIR, DBT_PROFILE_NAME, HELPER_SCRIPT


dbt_run_command = "dbt run --select example -t prd"


run_dbt_demo_dag = DbtShellTask(
    command=dbt_run_command, 
    helper_script=HELPER_SCRIPT, 
    profiles_dir=DBT_PROFILES_DIR, 
    profile_name=DBT_PROFILE_NAME, 
    name='DBT demo DAG',
    return_all=True,
    log_stderr=True)


flow_demo = Flow('Demo processing flow')
flow_demo.add_task(run_dbt_demo_dag)
