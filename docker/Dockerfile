FROM python:2.7-stretch

# https://github.com/phusion/baseimage-docker/issues/58
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
  locales \
  && rm -rf /var/lib/apt/lists/* \
  && locale-gen "en_US.UTF-8" \
  && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LC_ALL="en_US.UTF-8" LANG="en_US.utf8"

RUN apt-get update && apt-get install -y --no-install-recommends \
  apt-transport-https \
  apt-utils \
  bash-completion \
  ca-certificates \
  curl \
  dnsutils \
  freetype* \
  g++ \
  gfortran \
  git-core \
  gnupg \
  gpg-agent \
  graphviz \
  less \
  libblas-dev \
  libffi-dev \
  libgeos-dev \
  libgraphviz-dev \
  liblapack-dev \
  libproj-dev \
  libssl-dev \
  libxft-dev \
  libyaml-dev \
  netcat \
  pkg-config \
  proj-bin \
  unixodbc \
  unixodbc-dev \
  unzip \
  vim \
  wget \
  && rm -rf /var/lib/apt/lists/*

# docker (simple version), from https://docs.docker.com/engine/installation/linux/ubuntu
RUN curl -fsSL get.docker.com | sh

# standard requirements
COPY requirements.txt /
RUN pip install pip --upgrade \
  && pip install -r requirements.txt
# installed here rather than requirements because it doesn't list cython as a dependency, but fails
# if it doesn't have it
RUN pip install cartopy

# Jupyter & kernel gateway
ENV JUPYTER_USE_HTTPS='1' JUPYTER_NOTEBOOK_DIR='/notebooks'
# can't use env vars in `COPY`, so use two steps
COPY jupyter_notebook_config.py .jupyter/
RUN mv .jupyter $HOME/.jupyter
RUN jupyter notebook list

# Celery
ENV C_FORCE_ROOT=1

# gcloud
# from https://cloud.google.com/sdk/docs/#deb
# from https://code.google.com/p/google-cloud-sdk/issues/detail?id=691
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-stretch main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update && apt-get install -y --no-install-recommends \
  google-cloud-sdk \
  && rm -rf /var/lib/apt/lists/* \
  && git config --global credential.'https://source.developers.google.com'.helper gcloud.sh \
  && gcloud version
# if we use this image in cloud builder, it'll map the permissions in
ENV PATH=$PATH:/builder/google-cloud-sdk/bin/

# Mosek
RUN pip install -f https://download.mosek.com/stable/wheel/index.html Mosek \
  && python -c '__import__("mosek").Env()'

# sops
RUN curl -L https://github.com/mozilla/sops/releases/download/3.2.0/sops_3.2.0_amd64.deb --output sops.deb \
  && dpkg -i sops.deb \
  && rm sops.deb

# Airflow
# installed here rather than requirements to ensure dependency versions work
# don't install gcp_api here because it downgrades the version
# includes imperfect test to ensure it loads
# https://github.com/un33k/python-slugify/issues/52
ARG SLUGIFY_USES_TEXT_UNIDECODE=yes
RUN pip install apache-airflow[celery,postgres,crypto,s3]==1.10.2 \
  && airflow list_dags \
  # TODO: always return true until conflicts are resolved
  && pip check || true

ENV AIRFLOW_HOME=/usr/local/airflow
COPY airflow/airflow.cfg airflow/airflow_setup.py ${AIRFLOW_HOME}/
COPY airflow/airflow-entry.sh /usr/local/bin/
COPY airflow/dags.py ${AIRFLOW_HOME}/dags/
COPY airflow/airflow_local_settings.py ${AIRFLOW_HOME}/settings/
ENV PYTHONPATH="${AIRFLOW_HOME}/settings:${PYTHONPATH}"

CMD /bin/bash
