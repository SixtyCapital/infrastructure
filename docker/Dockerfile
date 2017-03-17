FROM ubuntu

RUN locale-gen "en_US.UTF-8" && locale-gen "en_US.UTF-8"

RUN apt-get update && apt-get install -y \
  apt-transport-https \
  apt-utils \
  bash-completion \
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
  python-pip \
  unixodbc \
  unixodbc-dev \
  vim \
  wget

# install mssql drivers https://msdn.microsoft.com/en-us/library/hh568454(v=sql.110).aspx

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install  -y \
  msodbcsql \
  mssql-tools

RUN ln -sfn /opt/mssql-tools/bin/sqlcmd-13.0.1.0 /usr/bin/sqlcmd
RUN ln -sfn /opt/mssql-tools/bin/bcp-13.0.1.0 /usr/bin/bcp


# Tini for Jupyter
ARG TINI_VERSION=v0.10.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini


# standard requirements
RUN pip install pip --upgrade
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN rm requirements.txt


# Jupyter
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py
RUN mv .jupyter $HOME/.jupyter
ENV JUPYTER_USE_HTTPS='1'
ENV JUPYTER_NOTEBOOK_DIR='/notebooks'


# Celery
ENV C_FORCE_ROOT=1


# Kernel-gateway
ENV KG_LIST_KERNELS=True


# gcloud
# from https://cloud.google.com/sdk/docs/#deb
# from https://code.google.com/p/google-cloud-sdk/issues/detail?id=691
RUN export CLOUD_SDK_REPO="cloud-sdk-xenial"
# RUN apt-get install lsb-release
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-xenial main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y google-cloud-sdk


# Mosek binary
ENV MOSEK_VERSION 8.0.0.59
ENV MOSEK_PATH /mosek/8/tools/platform/linux64x86
ENV MOSEKLM_LICENSE_FILE /mosek.lic
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:$MOSEK_PATH/bin
RUN curl http://download.mosek.com/stable/8.0.0.59/mosektoolslinux64x86.tar.bz2 > mosek.tar.bz2
RUN tar xf mosek.tar.bz2 && ln -s $MOSEK_PATH/bin/mosek /usr/bin/mosek && mosek -f
RUN cd $MOSEK_PATH/python/2 && python setup.py install --user && \
	python -c '__import__("mosek").Env()'
COPY mosek.lic /mosek.lic
