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
- sender: listens rabbitmq container and sends messages to clients
- dozzle: collects logs from all containers

