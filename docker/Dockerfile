FROM ubuntu

RUN apt-get update && apt-get install -y --no-install-recommends \
 locales \
 && rm -rf /var/lib/apt/lists/* \
 && locale-gen "en_US.UTF-8" && locale-gen "en_US.UTF-8"

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
  && rm -rf /var/lib/apt/lists/*

# install mssql drivers https://msdn.microsoft.com/en-us/library/hh568454(v=sql.110).aspx
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
  msodbcsql \
  mssql-tools \
  && rm -rf /var/lib/apt/lists/*
RUN ln -sfn /opt/mssql-tools/bin/sqlcmd-13.0.1.0 /usr/bin/sqlcmd \
 && ln -sfn /opt/mssql-tools/bin/bcp-13.0.1.0 /usr/bin/bcp

# Tini for Jupyter
ADD https://github.com/krallin/tini/releases/download/v0.14.0/tini /tini
RUN chmod +x /tini

# docker, from https://docs.docker.com/engine/installation/linux/ubuntu
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg |  apt-key add - \
  && add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  && apt-get update && apt-get install -y --no-install-recommends \
  docker-ce \
  && rm -rf /var/lib/apt/lists/*

# standard requirements
COPY requirements.txt /
RUN pip install pip --upgrade \
 && pip install setuptools \
 && pip install -r requirements.txt \
 && rm requirements.txt

# Jupyter & kernel gateway
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py
RUN mv .jupyter $HOME/.jupyter
ENV JUPYTER_USE_HTTPS='1' JUPYTER_NOTEBOOK_DIR='/notebooks' KG_LIST_KERNELS=True

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
 && git config --global credential.helper gcloud.sh
# if we use this image in cloud builder, it'll map the permissions in
ENV PATH=$PATH:/builder/google-cloud-sdk/bin/

# Mosek binary
ENV MOSEK_VERSION=8.0.0.59 MOSEK_PATH=/mosek/8/tools/platform/linux64x86 MOSEKLM_LICENSE_FILE=/mosek.lic
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MOSEK_PATH/bin
RUN curl http://download.mosek.com/stable/8.0.0.59/mosektoolslinux64x86.tar.bz2 > mosek.tar.bz2 \
 && tar xf mosek.tar.bz2 && ln -s $MOSEK_PATH/bin/mosek /usr/bin/mosek && mosek -f \
 && cd $MOSEK_PATH/python/2 && python setup.py install --user \
 && python -c '__import__("mosek").Env()'
COPY mosek.lic /mosek.lic

# Airflow
RUN pip install --upgrade --upgrade-strategy only-if-needed git+https://github.com/apache/incubator-airflow@1.8.2rc2
ENV AIRFLOW_HOME=/usr/local/airflow
COPY airflow/airflow.cfg airflow/airflow_setup.py ${AIRFLOW_HOME}/
COPY airflow/airflow-entry.sh /usr/local/bin/
COPY airflow/dags.py ${AIRFLOW_HOME}/dags/
