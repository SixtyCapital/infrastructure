# originally from https://github.com/puckel/docker-airflow/blob/master/Dockerfile
FROM gcr.io/sixty-capital/base:pandas-0.20.1

RUN apt-get update -y \
    && apt-get install -y netcat \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

ENV AIRFLOW_VERSION=1.8.1
ENV AIRFLOW_HOME=/usr/local/airflow

RUN pip install apache-airflow[celery,mssql,postgres,crypto,s3,gcp_api]==$AIRFLOW_VERSION

RUN pip install --upgrade --upgrade-strategy only-if-needed git+https://github.com/apache/incubator-airflow@1.8.2rc2

COPY airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY airflow_setup.py ${AIRFLOW_HOME}/airflow_setup.py
COPY airflow-entry.sh /usr/local/bin/airflow-entry.sh
