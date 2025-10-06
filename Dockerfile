FROM python:3.12-slim as python_base
RUN pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./ /usr/app/pipelines/
WORKDIR /usr/app/pipelines

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]