FROM python:3.10

WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y gdal-bin libpq-dev

# RUN apt-get install --only-upgrade libpq5

RUN curl -fsSL https://get.docker.com | sh
# VOLUME /var/run/docker.sock

# install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
