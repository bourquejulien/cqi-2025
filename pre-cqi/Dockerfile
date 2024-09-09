FROM python:3.12-alpine3.20 AS base

WORKDIR /app

RUN pip install pyarmor==8.5.11

COPY *.py .
RUN pyarmor gen .

FROM python:3.12-alpine3.20 AS final

ARG PORT=5000
EXPOSE $PORT

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

COPY --chown=cqi:cqi start.sh .
COPY --chown=cqi:cqi ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY --from=base --chown=cqi:cqi /app/dist .
USER cqi

ENTRYPOINT [ "sh", "start.sh" ]
