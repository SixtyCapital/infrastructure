FROM python:2

# COPY odbcinst.ini /etc/odbcinst.ini

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
