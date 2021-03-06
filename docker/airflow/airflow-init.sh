#!/usr/bin/env bash

# this is now only used for production, since https://github.com/SixtyCapital/sixty/pull/1441
# from https://github.com/mumoshu/kube-airflow/blob/master/script/entrypoint.sh

set -e
TRY_LOOP="20"

# we use celery redis but this only sets if not externally set
: ${REDIS_HOST:="redis"}
: ${REDIS_PORT:="6379"}
: ${REDIS_PASSWORD:=""}

: ${POSTGRES_HOST:="postgres"}
: ${POSTGRES_PORT:="5432"}

# Wait for Postresql
i=0
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT >/dev/null 2>&1 < /dev/null; do
  i=$((i+1))
  echo "$(date) - waiting for ${POSTGRES_HOST}:${POSTGRES_PORT}... $i/$TRY_LOOP"
  if [ $i -ge $TRY_LOOP ] ; then
    echo "$(date) - ${POSTGRES_HOST}:${POSTGRES_PORT} still not reachable, giving up"
    exit 1
  fi
  sleep 5
done
echo "Initialize database..."
airflow initdb

# Wait for Redis

# don't wait for redis if you don't need to (this is dependent on executor being set with an env. Possible to set with
# other config settings, and then this process won't recognize)
j=0
while ! nc -z $REDIS_HOST $REDIS_PORT >/dev/null 2>&1 < /dev/null; do
  j=$((j+1))
  if [ $j -ge $TRY_LOOP ]; then
    echo "$(date) - $REDIS_HOST still not reachable, giving up"
    exit 1
  fi
  echo "$(date) - waiting for Redis... $j/$TRY_LOOP"
  sleep 5
done