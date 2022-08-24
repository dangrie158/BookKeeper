FROM python:3.10-alpine

RUN apk add python3-dev build-base linux-headers pcre-dev libffi-dev git && \
    pip install poetry

RUN mkdir /bookkeeper
WORKDIR /bookkeeper

COPY poetry.lock pyproject.toml /bookkeeper/
RUN poetry install --no-dev --no-interaction

COPY . /bookkeeper/

CMD sh -c "poetry run python manage.py collectstatic --noinput && \
    poetry run python manage.py migrate && \
    poetry run gunicorn --config deploy/web/gunicorn.conf.py bookkeeper.wsgi"
