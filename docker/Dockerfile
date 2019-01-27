FROM python:3.6
MAINTAINER  William Hayes whayes@openbel.org

EXPOSE 8000

RUN pip3 install pipenv

RUN groupadd -g 1000 api && useradd api -u 1000 -g 1000 && mkdir /app && chown -R api:api /app

WORKDIR /app

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# -- Install dependencies:
RUN set -ex && pipenv install --deploy --system

COPY ./biosearch /app

USER api

CMD [ "python", "/app/main.py" ]
