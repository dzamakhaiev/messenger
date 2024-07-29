[![codecov.io](https://codecov.io/gh/)](https://codecov.io/gh/dzamakhaiev/messenger)
This is a simple REST API messenger application.


### Hardware requirements
- 2 or more CPU cores
- 1 GB or more free disk space
- 500 MB or more free RAM space


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

### List of endpoints
- `/api/health/`: Simple application availability check.
- `/api/users/`: Main endpoint for manipulating User instances (create, get, delete for now).
- `/api/login/`: Endpoint for user authentication.
- `/api/logout/`: Endpoint for user logging out.
- `/api/messages/`: Main endpoint for message exchange. 

### Endpoints schema
1. Health Check  
     Request:
     ```
     HEAD https://localhost:5000/api/health/
     ```
     Response: STATUS_CODE 200. TEXT: OK.  

2. Create User  
     Request:
     ```
     POST https://localhost:5000/api/users/
     HEADERS = {"Content-type": "application/json"}
     JSON: {"username": "unique username", "phone_number": "unique phone number", "password": "some password"}
     ```
     Response: STATUS_CODE 201. JSON: {"user_id": "unique user integer id"}.  

3. Get User Details  
     Request:
     ```
     GET https://localhost:5000/api/users/
     HEADERS = {"Content-type": "application/json", "Authorization": "Bearer token"}
     JSON: {"username": "username of needed user"}
     ```
     Response: STATUS_CODE 200. JSON: {"user_id": "unique user integer id", "public_key": "public key to encrypt messages"}.

4. Delete User  
     Request:
     ```
     DELETE https://localhost:5000/api/users/
     HEADERS = {"Content-type": "application/json"}
     JSON: {"user_id": "unique user id"}
     ```
     Response: STATUS_CODE 200. TEXT: User deleted.  

5. User Login  
     Request:
     ```
     POST https://localhost:5000/api/login/
     HEADERS = {"Content-type": "application/json"}
     JSON: {"username": "unique username", "password": "some password", "user_address": "ip address to send messages", "public_key": "public key to encrypt messages for that user"}
     ```
     Response: STATUS_CODE 200. JSON: {"user_id": "unique user integer id", "token": "token access to protected endpoints"}.

6. User Logout  
     Request:
     ```
     POST https://localhost:5000/api/logout/
     HEADERS = {"Content-type": "application/json", "Authorization": "Bearer token"}
     JSON: {"username": "unique username"}
     ```
     Response: STATUS_CODE 200. JSON: {"msg": "Logout successful.", "username": "unique username"}.  

7. Send Encrypted Message  
     Request:
     ```
     POST https://localhost:5000/api/messages/
     HEADERS = {"Content-type": "application/json", "Authorization": "Bearer token"}
     JSON: {"message": "encrypted message itself", "sender_id": "unique user integer id", "sender_username": "unique username", "receiver_id": "unique user integer id", "send_date": "when message sent in datetime format"}
     ```
     Response: STATUS_CODE 200. TEXT: Message processed.
