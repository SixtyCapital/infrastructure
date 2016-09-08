FROM 491722570113.dkr.ecr.us-east-1.amazonaws.com/base

RUN pip install jupyter --upgrade

USER root
# not sure this is strictly needed and could break if upstream changes
# WORKDIR /root

RUN mkdir .jupyter

COPY jupyter.pem .jupyter/notebook.pem
COPY jupyter_notebook_config.py .jupyter/jupyter_notebook_config.py

ENV USE_HTTPS='1'
ENV PASSWORD='sha1:565fbfe50026:3e4bb53af206d4835b158e23f669e90b92d2bbc8'

EXPOSE 8888

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix

CMD ["jupyter-notebook"]

# NB: docker uses tini & suggests this way might create kernel crashes. We can assess.
