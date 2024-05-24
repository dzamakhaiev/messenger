FROM python:3-alpine
EXPOSE 5000
COPY server_side /app/server_side
COPY requirements.txt /app
RUN rm /app/server_side/database/database.sqlite
VOLUME ["/app/server_side/database"]
VOLUME ["/app/server_side/logs"]
WORKDIR /app
RUN pip3 install -r requirements.txt --break-system-packages
WORKDIR /app/server_side/app/
CMD gunicorn -w 4 -b 0.0.0.0:5000 'listener:app'
