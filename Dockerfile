FROM ubuntu
USER root
EXPOSE 5000
COPY server_side /app/server_side
COPY requirements.txt /app
WORKDIR /app
RUN ["apt", "update"]
RUN ["apt", "install", "python3", "-y"]
RUN ["apt", "install", "python3-pip", "-y"]
RUN ["pip3", "install", "-r", "requirements.txt", "--break-system-packages"]
WORKDIR /app/server_side/app/
CMD ["python3", "listener.py"]