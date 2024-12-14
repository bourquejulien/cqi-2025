FROM python:3.12-alpine3.20 AS base

ARG USE_PYARMOR=false

WORKDIR /app

RUN apk add --no-cache build-base && \
    pip install --no-cache-dir pyarmor==8.5.11 && \
    python -m pip install --upgrade build

COPY . .

# Offuscate the python code
RUN if [ $USE_PYARMOR = "true" ] ; then pyarmor gen . && cp -r ./dist /dist ; else cp -r /app /dist ; fi 

FROM python:3.12-alpine3.20 AS final

RUN addgroup \
    --gid 10001 \
    cqi \
    && adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --ingroup cqi \
    --no-create-home \
    --uid 10000 \
    cqi

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY --from=base --chown=cqi:cqi /dist .

USER root

ENV SERVER_ADDRESS="https://server.cqiprog.info"
ENTRYPOINT [ "python", "app.py" ]
