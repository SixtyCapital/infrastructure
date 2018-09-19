FROM ubuntu:17.10

# https://github.com/phusion/baseimage-docker/issues/58
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
  locales \
  && rm -rf /var/lib/apt/lists/* \
  && locale-gen "en_US.UTF-8"

ENV LC_ALL="en_US.UTF-8" LANG="en_US.utf8"

RUN apt-get update && apt-get install -y --no-install-recommends \
  apt-transport-https \
  apt-utils \
  bash-completion \
  ca-certificates \
  curl \
  dialog \
  freetype* \
  g++ \
  gfortran \
  git-core \
  libblas-dev \
  libffi-dev \
  liblapack-dev \
  libssl-dev \
  libxft-dev \
  libyaml-dev \
  linux-image-extra-virtual \
  python-pip \
  python-dev \
  software-properties-common \
  unixodbc \
  unixodbc-dev \
  vim \
  wget \
  netcat \
  dnsutils \
  libgraphviz-dev \
  graphviz \
  proj-bin \
  libproj-dev \
  libgeos-dev \
  unzip \
  && rm -rf /var/lib/apt/lists/*

# install mssql drivers https://msdn.microsoft.com/en-us/library/hh568454(v=sql.110).aspx
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/ubuntu/17.10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
  msodbcsql17 \
  mssql-tools \
  && rm -rf /var/lib/apt/lists/*
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile

# docker (simple version), from https://docs.docker.com/engine/installation/linux/ubuntu
RUN curl -fsSL get.docker.com | sh

# standard requirements
COPY requirements.txt /
RUN curl https://bootstrap.pypa.io/get-pip.py | python \
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
ARG CLOUD_SDK_REPO="cloud-sdk-xenial"
# RUN apt-get install lsb-release
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-xenial main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
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

# Airflow
# installed here rather than requirements to ensure dependency versions work
# don't install gcp_api here because it downgrades the version
# includes imperfect test to ensure it loads
# https://github.com/un33k/python-slugify/issues/52
ARG SLUGIFY_USES_TEXT_UNIDECODE=yes
RUN pip install apache-airflow[celery,postgres,crypto,s3]==1.10.0 \
  && airflow list_dags \
  # TODO: always return true until conflicts are resolved
  && pip check || true
# TODO: check if needed
RUN pip install google-auth-httplib2

ENV AIRFLOW_HOME=/usr/local/airflow
COPY airflow/airflow.cfg airflow/airflow_setup.py ${AIRFLOW_HOME}/
COPY airflow/airflow-entry.sh /usr/local/bin/
COPY airflow/dags.py ${AIRFLOW_HOME}/dags/
COPY airflow/airflow_local_settings.py ${AIRFLOW_HOME}/settings/
ENV PYTHONPATH="${AIRFLOW_HOME}/settings:${PYTHONPATH}"

CMD /bin/bash
