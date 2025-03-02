# Starting the Image Processing Microservice

## Prerequisites

- Python3.8 or above
- Docker

## Project Setup

```shell
git clone https://github.com/jannatul29/image-processing-microservice.git
Copy `app.conf.sample` file from `config` directory and create `app.conf` in the same directory
Open file `config/app.conf` and put appropriates credentials
make virtualenv
source env/bin/activate
pip3 install -r requirements.txt
```

## Making Future Model Changes
```shell
alembic revision --autogenerate -m "Describe the change"
alembic upgrade head
```

## Deployment

Run in local

```shell
celery -A services.celery_worker worker --loglevel=info
celery -A services.celery_worker.celery flower --loglevel=info --port=5555
uvicorn core.app:app --reload
```

Run in Docker

```shell
docker-compose up --build
```

## Swagger UI

http://127.0.0.1:8000/docs

## Task Tracking UI

http://127.0.0.1:5555

## Process Multiple Image

```shell
bash run_image_processor.sh
```