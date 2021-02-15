FROM python:3.7.3

WORKDIR /src

RUN pip install pre-commit
#
## Install build dependencies
RUN pip install pipenv
COPY Pipfile /src/Pipfile
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt
