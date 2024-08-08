FROM python:3.11-alpine as base

COPY . /srv
WORKDIR /srv

RUN rm -rf /srv/frontend/node_modules /srv/**/__pycache__ /srv/**/*.pyc

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache dos2unix libpq-dev netcat-openbsd chrony supervisor && \
    python -m pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    cd /srv/backend && \
    poetry install --no-root && \
    dos2unix /srv/entrypoint.sh && \
    chmod +x /srv/entrypoint.sh && \
    dos2unix /srv/entrypoint_celery.sh && \
    chmod +x /srv/entrypoint_celery.sh && \
    mkdir -p /srv/data/cache/ /srv/data/temp/ /srv/data/rabbitmq/ /srv/logs/ && \
    chmod -R 777 /srv/data/cache/ /srv/data/temp/ /srv/data/rabbitmq/ /srv/logs/ && \
    echo "server pool.ntp.org iburst" >> /etc/chrony/chrony.conf

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#############
# PROJECT #
#############
FROM base as project
ENTRYPOINT ["sh", "/srv/entrypoint.sh"]

#############
# CELERY #
#############
FROM base as celery
ENTRYPOINT ["sh", "/srv/entrypoint_celery.sh"]
