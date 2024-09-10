#!/bin/sh

if [ -z ${PORT+x} ]; then
    PORT=5000
fi

exec gunicorn -w 1 -b 0.0.0.0:$PORT --access-logfile "-" "app:start_gunicorn()"
