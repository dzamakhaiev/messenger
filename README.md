This is a simple REST API messenger application.


### Hardware requirements
- 2 or more CPU cores
- 1 GB or more free disk space
- 1 GBor more free RAM space


### Software requirements
- docker
- docker-compose

### How to run
- docker-compose -f .\messenger.yaml up

### Containers structure
- nginx: entry point for entire application. Also works as balancer. Redirects https requests as http requests 
to other container(s) "listener".
- listener: one or more containers that process client's requests. Number of listeners could be changed in
docker-compose yaml file.
- postgres: main SQL database for application.
- rabbitmq: messages/events broker that passes them to "sender" container(s).
- sender: listens rabbitmq container and sends messages to clients.
- dozzle: collects logs from all containers.

### Entry point setup
By default, Nginx server listens 5000 port for https requests.
Nginx https server needs a valid certificate. That application uses self-signed certificate for 
demonstration purpose. Put your valid certificate file to "cert" directory:
- cert/certificate.pem
- cert/private_key.pem

Main Nginx config items:
- worker_processes N: depends on your CPU cores number.
- upstream listener: list of "listener" containers for redirected requests. Number of listeners 
could be changed.
- zone=limit:100m rate=100r/s: 100 mb buffer to keep client's requests that overcome 
maximum request rate (100 requests per second by default).
- zone=limit burst=1000: length of queue for extra requests that overcome current maximum rate.

