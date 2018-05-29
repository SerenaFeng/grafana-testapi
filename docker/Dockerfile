FROM alpine:3.7

RUN apk --no-cache add --update \
        python python-dev py-pip bash vim git libffi-dev

RUN pip install --no-cache-dir --src /home \
    -e git+https://github.com/serenafeng/grafana-testapi.git#egg=grafana-testapi

CMD ["pecan", "serve", "/home/grafana-testapi/config.py"]