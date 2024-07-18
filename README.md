This is a simple REST API messenger application.


### Hardware requirements
- 2 or more CPU cores
- 1 GB or more free disk space
- 1 GB or more free RAM space


### Software requirements
- Docker
- docker-compose

### How to run
Execute the following command:
- docker-compose -f .\messenger.yaml up

### Containers structure
- **nginx**: The entry point for the entire application. Also serves as a balancer, redirecting HTTPS requests 
to HTTP requests for other container(s) ("listener").
- **listener**: One or more containers that process client requests. The number of listeners can be 
adjusted in the docker-compose YAML file.
- **postgres**: The main SQL database for the application.
- **rabbitmq**: A message/events broker that passes messages to the "sender" container(s).
- **sender**: Listens to the RabbitMQ container and sends messages to clients.
- **dozzle**: Collects logs from all containers.
 
### Entry point setup
The Nginx HTTPS server requires a valid certificate. For demonstration purposes, 
this application uses a self-signed certificate. If you have a valid certificate, 
place the certificate file in the "cert" directory:
- cert/certificate.pem
- cert/private_key.pem

Main Nginx config items:
- `worker_processes N`: Adjust based on your CPU core count.
- `upstream listener`: List of "listener" containers for redirected requests. 
The number of listeners can be changed.
- `zone=limit:100m rate=100r/s`: A 100 MB buffer to handle client requests that exceed 
the maximum request rate (default is 100 requests per second).
- `zone=limit burst=1000`: The length of the queue for extra requests that exceed 
the current maximum rate.

