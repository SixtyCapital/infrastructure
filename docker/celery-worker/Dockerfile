FROM 491722570113.dkr.ecr.us-east-1.amazonaws.com/base

ENV C_FORCE_ROOT=1

ENTRYPOINT ["celery", "-A", "sixty.compute.celery_app"]
CMD ["worker"]
