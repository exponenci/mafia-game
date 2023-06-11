FROM python:3.9-alpine

COPY ./ /client

WORKDIR /client

RUN mkdir outs
RUN mkdir outs/core

RUN pip install -r requirements.txt
