FROM python:3.12

RUN mkdir /app

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY *.py .

ENTRYPOINT [ "/app/app.py" ]
