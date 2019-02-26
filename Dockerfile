FROM python:3-alpine

RUN apk update \
	&& apk add --virtual build-dependencies \
	build-base gcc 

ADD . /app

RUN pip install -U pip 

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/node_exporter.py"]
