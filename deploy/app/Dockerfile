FROM nginx:alpine
COPY app /usr/share/nginx/html
COPY train/*.json /usr/share/nginx/html/train/
COPY deploy/app/entrypoint.sh /usr/share/nginx/html/entrypoint.sh
RUN chmod 755 /usr/share/nginx/html/entrypoint.sh

WORKDIR /usr/share/nginx/html

ENTRYPOINT ["/usr/share/nginx/html/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
