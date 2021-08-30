FROM python:latest

WORKDIR /fudgecake/onyx
COPY ./requirements.txt /fudgecake/onyx/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /fudgecake/onyx

WORKDIR /fudgecake/onyx
CMD "python3", "-m", "src.onyx.nepse"