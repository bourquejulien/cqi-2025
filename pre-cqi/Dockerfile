FROM python:3.12 AS base

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY *.py .

FROM python:3.12-slim AS final

ENV PORT=5000
RUN groupadd -g 10001 cqi && useradd -u 10000 -g cqi cqi

WORKDIR /app

COPY --from=base --chown=cqi:cqi /app/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY --from=base --chown=cqi:cqi /app .
COPY --chown=cqi:cqi start.sh .
USER cqi

ENTRYPOINT [ "sh", "start.sh" ]
