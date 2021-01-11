#!/usr/bin/env bash

# --------------------------------------------------------------------------------------------------
# start web service to provide rest end points for this container
# --------------------------------------------------------------------------------------------------

gunicorn --pythonpath / -b 0.0.0.0:$SERVICE_PORT -k gevent -t $SERVICE_TIMEOUT -w $WORKER_COUNT intel_platform.deployment.server:app -k uvicorn.workers.UvicornWorker

# --------------------------------------------------------------------------------------------------
# to make the container alive for indefinite time
# --------------------------------------------------------------------------------------------------
#touch /tmp/a.txt
#tail -f /tmp/a.txt



