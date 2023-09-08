FROM python:3.10 as base

ENV DJANGO_READ_DOT_ENV_FILE True
ENV PYTHONUNBUFFERED 1
WORKDIR /app


RUN apt-get update -y && apt-get upgrade -y && \
  apt-get install -y gcc=4:10.2.1-1 python3-dev=3.9.2-3 \
  default-mysql-client=1.0.7 default-libmysqlclient-dev=1.0.7 --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]