FROM ubuntu:20.04
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update -qq && \
    apt-get install -qq -y --no-install-recommends  wget gnupg2 vim git curl && \
    apt-get install -y --no-install-recommends python3-pip python3-dev && \
    apt-get clean

RUN pip3 install setuptools wheel
