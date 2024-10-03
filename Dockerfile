FROM python:3.10

WORKDIR /catshow_app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY config.py .
COPY database.py .
COPY main.py .
COPY models.py .
COPY schemas.py .
