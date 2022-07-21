FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY bookkeeper.nginx.conf /etc/nginx/sites-available/bookkeeper.nginx.conf
RUN mkdir /etc/nginx/sites-enabled &&\
    ln -s /etc/nginx/sites-available/bookkeeper.nginx.conf /etc/nginx/sites-enabled/
CMD ["nginx", "-g", "daemon off;"]
