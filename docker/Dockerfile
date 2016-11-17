FROM python:2

RUN apt-get update && apt-get install -y \
  bash-completion \
  freetds-bin \
  freetds-dev \
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
  # python-dev
  # python3-dev
  # python3-setuptools
  # python-setuptools
  tdsodbc \
  unixodbc-dev \
  vim

COPY requirements.txt /
RUN pip install -r requirements.txt
RUN rm requirements.txt

# Jupyter

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py
RUN mv .jupyter $HOME/.jupyter
# needed because of spawning, according to Jupyter
ARG TINI_VERSION=v0.10.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENV USE_HTTPS='1'
# standard sixty password. Can pass others with PASSWORD or
# http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#preparing-a-hashed-password
ENV PASSWORD_HASH='sha1:e641696b1d4a:6fae0db560beb06450d7fb5af6d83ca627130d30'
ENV NOTEBOOK_DIR='/notebooks'

# Celery
ENV C_FORCE_ROOT=1
