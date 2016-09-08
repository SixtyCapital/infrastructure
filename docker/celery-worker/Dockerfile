FROM 491722570113.dkr.ecr.us-east-1.amazonaws.com/base

COPY celeryd_default etc/default/celeryd
COPY celeryd_init /etc/init.d/celeryd

RUN update-rc.d celeryd defaults
RUN update-rc.d celeryd enable

CMD "celery -A sixty.compute.setup worker -l info 2>&1 | tee ~/workspace/celery.log"
