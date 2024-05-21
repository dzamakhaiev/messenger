FROM python:3-alpine
EXPOSE 5000-5010
COPY server_side /app/server_side
COPY requirements.txt /app
RUN rm /app/server_side/database/database.sqlite
WORKDIR /app
RUN pip3 install -r requirements.txt --break-system-packages
WORKDIR /app/server_side/app/
CMD python3 listener.py
