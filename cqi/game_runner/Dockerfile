FROM python:3.12-alpine3.20 AS base

ARG USE_PYARMOR=false

RUN apk add --no-cache build-base && \
    pip install --no-cache-dir pyarmor==8.5.11 && \
    python -m pip install --upgrade build