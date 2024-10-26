FROM python:3.12-alpine3.20 AS base

WORKDIR /app

RUN apk add --no-cache build-base && pip install --no-cache-dir pyarmor==8.5.11

COPY ./src ./src
COPY ./app.py .

# Offuscate the python code
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

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY --from=base --chown=cqi:cqi /app/dist .

RUN chmod +x app.py

USER cqi
ENV PORT=$PORT
ENV MODE=release

ENTRYPOINT [ "python", "app.py" ]
