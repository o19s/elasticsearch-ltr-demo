FROM worleydl/nginx-grunt:v1

# Copy source to host
COPY app /app
WORKDIR /app

# Get deps
#RUN npm install
#RUN bower --allow-root install -g

EXPOSE 8000

# Start python
CMD /app/srv.sh
