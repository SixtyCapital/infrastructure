FROM python:3.6-stretch

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
  graphviz-dev \
  less \
  libblas-dev \
  libffi-dev \
  libgeos-dev \
  libgraphviz-dev \
  liblapack-dev \
  libproj-dev \
  libssl-dev \
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

# install mssql drivers https://msdn.microsoft.com/en-us/library/hh568454(v=sql.110).aspx
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
  msodbcsql17 \
  mssql-tools \
  && rm -rf /var/lib/apt/lists/*
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile

# docker (simple version), from https://docs.docker.com/engine/installation/linux/ubuntu
RUN curl -fsSL get.docker.com | sh

# standard requirements
COPY requirements.txt /
RUN pip install pip --upgrade \
  # https://github.com/un33k/python-slugify/issues/52
  && pip install --no-cache -r requirements.txt \
  # TODO: always return true until conflicts are resolved
  && pip check || true
# https://github.com/antocuni/pdb/issues/58
# remove at Py3
RUN pip uninstall -y pyrepl

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
# currently resolves to 35.185.107.128
ENV MOSEKLM_LICENSE_FILE="8888@mosek.sixty.capital:/home/ubuntu/5054.lic"
RUN pip install -f https://download.mosek.com/stable/wheel/index.html Mosek \
  && python -c '__import__("mosek").Env()'

# sops
RUN curl -L https://github.com/mozilla/sops/releases/download/3.2.0/sops_3.2.0_amd64.deb --output sops.deb \
  && dpkg -i sops.deb \
  && rm sops.deb

# kubectl
# TODO: consider installing as part of gcloud
# https://kubernetes.io/docs/tasks/tools/install-kubectl/#kubectl-install-1
RUN apt-get update && apt-get install -y apt-transport-https \ 
  && curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list \
  && apt-get update && apt-get install -y \ 
  kubectl \ 
  && rm -rf /var/lib/apt/lists/*  
# && kubectl version

# kustomize
# https://hub.docker.com/r/bitlayer/kustomize/dockerfile
# update to use kubectl when available more standard https://cloud.google.com/sdk/docs/release-notes
RUN curl -L https://github.com/kubernetes-sigs/kustomize/releases/download/v2.0.3/kustomize_2.0.3_linux_amd64 \
  -o /usr/bin/kustomize \
  && chmod +x /usr/bin/kustomize

ENV AIRFLOW_HOME=/usr/local/airflow
COPY airflow/airflow.cfg airflow/airflow-init.sh ${AIRFLOW_HOME}/
COPY airflow/airflow_local_settings.py ${AIRFLOW_HOME}/settings/
ENV PYTHONPATH="${AIRFLOW_HOME}/settings:${PYTHONPATH}"
RUN python -c "import airflow"

CMD /bin/bash
