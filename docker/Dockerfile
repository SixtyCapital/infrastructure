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
COPY requirements.txt /
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
RUN rm requirements.txt


# Jupyter
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py
RUN mv .jupyter $HOME/.jupyter
ENV JUPYTER_USE_HTTPS='1'
# Can pass a password with either JUPYTER_PASSWORD or JUPYTER_PASSWORD_HASH
# http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#preparing-a-hashed-password
ENV JUPYTER_NOTEBOOK_DIR='/notebooks'


# Celery
ENV C_FORCE_ROOT=1


# Kernel-gateway
ENV KG_LIST_KERNELS=True
