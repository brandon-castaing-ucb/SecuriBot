FROM alpine

EXPOSE 1883

RUN apk update && apk add mosquitto

ENTRYPOINT /usr/sbin/mosquitto 
