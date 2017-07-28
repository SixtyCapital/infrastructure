#!/usr/bin/env bash

AIRFLOW_HOME="/usr/local/airflow"
CMD="/usr/local/bin/airflow"
TRY_LOOP="20"

: ${REDIS_HOST:="redis"}
: ${REDIS_PORT:="6379"}
: ${REDIS_PASSWORD:=""}

#
# : ${POSTGRES_HOST:="postgres"}
: ${POSTGRES_PORT:="5432"}
# : ${POSTGRES_USER:="airflow"}
# : ${POSTGRES_PASSWORD:="airflow"}
# : ${POSTGRES_DB:="airflow"}
#
# : ${FERNET_KEY:=$(python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)")}

# Wait for Postresql
if [ "$1" = "webserver" ] || [ "$1" = "worker" ] || [ "$1" = "scheduler" ] ; then
  i=0
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT >/dev/null 2>&1 < /dev/null; do
    i=$((i+1))
    if [ "$1" = "webserver" ]; then
      echo "$(date) - waiting for ${POSTGRES_HOST}:${POSTGRES_PORT}... $i/$TRY_LOOP"
      if [ $i -ge $TRY_LOOP ]; then
        echo "$(date) - ${POSTGRES_HOST}:${POSTGRES_PORT} still not reachable, giving up"
        exit 1
      fi
    fi
    sleep 5
  done
  echo "Initialize database..."
  $CMD initdb
  python ${AIRFLOW_HOME}/airflow_setup.py
fi

# Wait for Redis
if [ "$1" = "webserver" ] || [ "$1" = "worker" ] || [ "$1" = "scheduler" ] || [ "$1" = "flower" ] ; then
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
fi

# avoid triggering CrashLoopBackOff in kubernetes sched with --num_runs
if [ "$1" = "scheduler" ] ; then
  while true; do
    $CMD "$@"
    ret=$?
    if [ $ret -ne 0 ]; then
      exit $?
    fi
  done
else
  $CMD "$@"
fi
