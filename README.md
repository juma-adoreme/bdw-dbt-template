# bdw-dbt-template
DBT project template for 2025 BDW workshop
- Install gcloud CLI: https://cloud.google.com/sdk/docs/install
- Login to GCP project: `gcloud auth login`
- Install uv: https://docs.astral.sh/uv/getting-started/installation/
- Init DBT
- Install jaffle shop data generator `pipx install jafgen`
- Generate data: `cd seeds; jafgen 3`

For the elementary setup
- Install elementary-data python package
- Check installation with `edr --version`
- Add in dbt folder packages.yml file
- Run `dbt deps` to install new package
- Run dbt models: `dbt run --select elementary`
- Generate HTML report: `edr report --profiles-dir dbt/`
