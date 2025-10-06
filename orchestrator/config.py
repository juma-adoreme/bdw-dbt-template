import os
import yaml
import logging


config_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config.yml")
    )

try:
    with open(config_file_path) as file:
        configs = yaml.safe_load(file)
except Exception as e:
    if isinstance(e, FileNotFoundError):
        logging.critical({"message": f"Config file couldn't be found at: {config_file_path}!\n{str(e)}"})
    else:
        logging.critical({"message": f"An exception occurred while trying to load config file: {config_file_path}!\n{str(e)}"})
    raise e


DBT_PROFILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", configs["dbt"]["profiles_dir"]))
DBT_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", configs["dbt"]["project_root"]))
DBT_PROFILE_NAME = configs["dbt"]["profile_name"]
HELPER_SCRIPT = f"cd {DBT_PROJECT_DIR}"
SLACK_CHANNEL_ID = configs["slack"].get("channel_id")

if SLACK_CHANNEL_ID:
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    project_id = configs["gcp"]["project_id"]
    secret_name = configs["slack"].get("bot_secret_id")
    SLACK_BOT_SECRET_ID = configs["slack"].get("bot_secret_id")
    response = client.access_secret_version(name=f"projects/{project_id}/secrets/{secret_name}/versions/latest")
    SLACK_BOT_TOKEN = response.payload.data.decode("UTF-8")
else:
    SLACK_BOT_TOKEN = None