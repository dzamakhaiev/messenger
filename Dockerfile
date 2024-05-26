FROM python:3-alpine
EXPOSE 5000
COPY server_side/app /app/server_side/app
COPY server_side/logger /app/server_side/logger
COPY server_side/broker /app/server_side/broker
COPY server_side/database /app/server_side/database
COPY requirements.txt /app
RUN rm /app/server_side/database/database.sqlite
VOLUME ["/app/server_side/database"]
VOLUME ["/app/server_side/logs"]
WORKDIR /app
RUN pip3 install -r requirements.txt --break-system-packages
WORKDIR /app/server_side/app/
#CMD python sender.py
#ENTRYPOINT python listener.py
#CMD gunicorn -w 4 -b 0.0.0.0:5000 'listener:app'
