#!/bin/bash

if [ -z ${PORT+x} ]; then
    PORT=5000
fi

exec gunicorn -w 1 -b 0.0.0.0:$PORT "app:app"
