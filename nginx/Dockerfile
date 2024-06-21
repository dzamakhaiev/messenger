FROM nginx:stable-alpine
EXPOSE 443
EXPOSE 5000
COPY cert/certificate.pem /etc/nginx/ssl/certificate.pem
COPY cert/private_key.pem /etc/nginx/ssl/private_key.pem
COPY nginx/nginx.conf /etc/nginx/nginx.conf