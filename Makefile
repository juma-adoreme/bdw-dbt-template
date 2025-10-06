GCP_PROJECT := bigdataweek2025
GCP_SERVICE_ACCOUNT := prefect-runner@$(GCP_PROJECT).iam.gserviceaccount.com
RUN_SERVICE_NAME := prefect-dbt
REGISTRY = gcr.io/$(GCP_PROJECT)/$(RUN_SERVICE_NAME)
SERVICE_URL = gcloud run services list --platform managed --filter=$(RUN_SERVICE_NAME) --format='value(URL)'
REGION := us-east1
SLACK_BOT_TOKEN := slack_pbot_token

# uv-setup:
# 	uv init
# 	uv add dbt-bigquery
# 	uv add "prefect<2.0"
# 	uv add fastapi
# 	uv add uvicorn
# 	uv add slack-sdk
# 	uv add google-cloud-secret-manager
# 	uv add elementary-data
# 	uv pip compile pyproject.toml --output-file requirements.txt

# dbt-setup:
# 	dbt init 

run:
	uvicorn main:app --host 0.0.0.0  --port 8080 --reload

test-fastapi:
	curl --location 'http://localhost:8080/prefect' \
		--header 'Content-Type: application/json' \
		--data '{"flow_name": "flow_demo"}'

set-gcp:
# 	gcloud auth login
	gcloud auth application-default login 
	gcloud config set project $(GCP_PROJECT)

create-sa:
	gcloud iam service-accounts create prefect-runner --display-name="Prefect runner SA"

secrets-acces: 
	gcloud secrets add-iam-policy-binding $(SLACK_BOT_TOKEN) \
	--member=serviceAccount:$(GCP_SERVICE_ACCOUNT) \
	--role=roles/secretmanager.secretAccessor \
	--project=$(GCP_PROJECT)

bq-jobs-user:
	gcloud projects add-iam-policy-binding $(GCP_PROJECT) \
		--member=serviceAccount:$(GCP_SERVICE_ACCOUNT) \
		--role=roles/bigquery.jobUser

bq-data-user:
	gcloud projects add-iam-policy-binding $(GCP_PROJECT) \
		--member=serviceAccount:$(GCP_SERVICE_ACCOUNT) \
		--role=roles/bigquery.dataOwner

generate-reqs:
	uv pip compile pyproject.toml --output-file requirements.txt

deploy-prd:
	gcloud config set project $(GCP_PROJECT)
	gcloud builds submit --tag $(REGISTRY)
	
	gcloud run deploy $(RUN_SERVICE_NAME) \
    --image $(REGISTRY):latest \
    --service-account $(GCP_SERVICE_ACCOUNT) \
    --memory=4Gi \
    --max-instances=10 \
    --platform=managed \
    --region=$(REGION) \
    --timeout=1800s \
    --no-allow-unauthenticated

invoker: 
	gcloud run services add-iam-policy-binding $(RUN_SERVICE_NAME) \
	--member=serviceAccount:$(GCP_SERVICE_ACCOUNT) \
	--role=roles/run.invoker \
	--region=$(REGION) \
	--platform managed

gcp-token:
	gcloud auth print-identity-token