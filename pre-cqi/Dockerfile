FROM python:3.12-alpine3.20 AS base

WORKDIR /app

RUN apk add --no-cache build-base && \
    apk add --no-cache shc --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ && \
    pip install --no-cache-dir pyarmor==8.5.11

COPY ./src ./src
COPY ./app.py .
COPY ./start.sh .

# Obfuscate the start script and the python code
RUN shc -S -B -r -f start.sh -o start && pyarmor gen .

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
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=base /app/dist .
COPY --from=base ./app/start .

# Prevent user cqi from accessing the app files, make the start binary run as root
RUN chmod -R 770 /app && chmod 4771 /app/start
USER cqi

ENTRYPOINT [ "/app/start" ]
