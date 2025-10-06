# bdw-dbt-template
DBT project template for 2025 BDW workshop
- Install gcloud CLI: https://cloud.google.com/sdk/docs/install
- Login to GCP project: `gcloud auth application-default login`
- From this point, you can just create a virtual environment and install everything from `requirements.txt` (`pip install -r requirements.txt`)
- Install uv: https://docs.astral.sh/uv/getting-started/installation/ (Optional for python package & env management)
- Init DBT (Already in repo)
- Install jaffle shop data generator `pipx install jafgen` (Already in repo)
- Generate data: `cd seeds; jafgen 3` (Already in repo)

For the elementary setup (Already in repo, no need to rerun)
- Install `elementary-data` python package
- Check installation with `edr --version`
- Add in dbt folder packages.yml file
- Run `dbt deps` to install new package
- Run dbt models: `dbt run --select elementary`
- Generate HTML report: `edr report --profiles-dir dbt/`
