FROM python:3-alpine
EXPOSE 5000
ENV TZ=Europe/Athens
ENV RUN_INSIDE_DOCKER 1
ENV PATH=$PATH:/messenger
RUN apk update
RUN apk upgrade
RUN mkdir /messenger
WORKDIR /messenger
COPY ./server_side /messenger/server_side
COPY ./scripts /messenger/scripts
COPY ./logger /messenger/logger
COPY ./requirements.txt /messenger/requirements.txt
RUN pip3 install -r requirements.txt --break-system-packages
WORKDIR /messenger/server_side/app