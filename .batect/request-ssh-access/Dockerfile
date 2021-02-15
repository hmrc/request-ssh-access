# Stage: build
FROM python:3.7.3 AS build

WORKDIR /src

# Install build dependencies
RUN pip install pipenv
COPY Pipfile /src/Pipfile
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

COPY . /src/
RUN echo "0.0.0-rc0" > .version

# Build request-ssh-access
RUN tox

# Stage: run
FROM python:3.7.3 AS run

WORKDIR /src

COPY --from=build /src/.tox/dist/request-ssh-access-0.0.0rc0.zip /src/

RUN pip install request-ssh-access-0.0.0rc0.zip
