FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install pyzmq
COPY . /app

ENTRYPOINT ["python", "-u"]