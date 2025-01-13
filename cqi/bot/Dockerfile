FROM python:3.12-alpine3.20 AS base

ARG USE_PYARMOR=false
ARG BOT_LEVEL=medium

RUN apk add --no-cache build-base && \
    pip install --no-cache-dir pyarmor==8.5.11 && \
    python -m pip install --upgrade build

WORKDIR /app/game_server_common
COPY ./game_server_common .

RUN python -m build

WORKDIR /app/bot
COPY ./bot/src ./src
COPY ./bot/app.py .

RUN if [ $BOT_LEVEL = "medium" ] ; then echo "ENFORCE_EASY=True" > ./src/flag.py ; fi

# Offuscate the python code
RUN if [ $USE_PYARMOR = "true" ] ; then pyarmor gen . && cp -r ./dist /app/dist ; else cp -r /app/bot /app/dist ; fi 

FROM python:3.12-alpine3.20 AS final

ARG BOT_LEVEL
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

COPY ./bot/requirements.txt ./requirements.txt
RUN sed -i '$ d' requirements.txt && pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY --from=base --chown=cqi:cqi /app/game_server_common/dist/game_server_common-0.0.1-py3-none-any.whl .
RUN pip install game_server_common-0.0.1-py3-none-any.whl && rm game_server_common-0.0.1-py3-none-any.whl

COPY --from=base --chown=cqi:cqi /app/dist .

RUN chmod +x app.py

USER cqi
ENV PORT=$PORT
ENV MODE=release
ENV BOT_LEVEL=$BOT_LEVEL

ENTRYPOINT [ "python", "app.py" ]
