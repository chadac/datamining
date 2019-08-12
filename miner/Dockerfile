FROM python:3.7-alpine3.10

RUN apk --no-cache add procps

ENV home /home
ENV APP_FILE "app.py"
ENV MIN "*"
ENV HOUR "*"
ENV DAY "*"
ENV MONTH "*"
ENV WEEK "*"

WORKDIR /home

ADD requirements.txt /home/requirements.txt
RUN pip install -r requirements.txt

ADD entrypoint.sh /home/entrypoint.sh
ADD run-script.sh /home/run-script.sh

ENTRYPOINT ["/home/entrypoint.sh"]
