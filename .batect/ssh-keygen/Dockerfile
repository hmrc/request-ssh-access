FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
        openssh-client \
        && apt-get autoremove \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /src
