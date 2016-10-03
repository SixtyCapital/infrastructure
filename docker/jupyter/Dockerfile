FROM 491722570113.dkr.ecr.us-east-1.amazonaws.com/base

RUN pip install jupyter --upgrade
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

# needed because of spawning, according to Jupyter
ARG TINI_VERSION=v0.10.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py
RUN mv .jupyter $HOME/.jupyter

ENV USE_HTTPS='1'
# standard sixty password. Can pass others with PASSWORD or
# http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#preparing-a-hashed-password
ENV PASSWORD_HASH='sha1:e641696b1d4a:6fae0db560beb06450d7fb5af6d83ca627130d30'
ENV NOTEBOOK_DIR='~/notebooks'

EXPOSE 8888

CMD ["jupyter-notebook"]


# you want to map /notebooks to keep notebooks on the host. For example:
# docker run -ti -p 8888:8888 -v ~/drive/workspace/notebook:/notebooks $REGISTRY/jupyter
