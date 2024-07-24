FROM python:3-alpine
EXPOSE 5000
ENV RUN_INSIDE_DOCKER 1
RUN apk update
RUN apk upgrade
RUN apk add git
RUN git clone https://github.com/dzamakhaiev/messenger.git
WORKDIR /messenger
RUN pip3 install -r requirements.txt --break-system-packages
WORKDIR /messenger/server_side/app/
#CMD python sender.py
#CMD gunicorn -w 4 -b 0.0.0.0:5000 'listener:app'
