FROM python:3.6

MAINTAINER Alex Bierwagen <me@alexb.io>

# Put all the code in /usr/src/app
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# Copy just the requirements.txt to cache the build step in docker
COPY ./requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

# Signify that we are using docker so we can use docker specific settings
ENV DOCKER=1

EXPOSE 8000
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]