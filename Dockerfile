
FROM mongo:latest
LABEL maintainer="Paulo Amaral - paulo.security@gmail.com"

#python version
FROM python:3.7

#create folder
RUN mkdir -p /opt/projetos
RUN mkdir -p /opt/projetos/dev
RUN mkdir -p /opt/projetos/dev/rosa_crud

#Install dependencies
RUN apt-get update
RUN apt-get install -y python3-setuptools nano 
RUN apt-get install -y python3-pip
RUN pip3 install flask
RUN pip3 install pymongo 
RUN pip3 install flask-restful
RUN pip3 install requests
RUN pip3 install -U flask-cors

#Install dependencies
WORKDIR /opt/projetos/dev/rosa_crud
COPY requiremens.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the default port
EXPOSE 27017
EXPOSE 8080

# Default port to execute the entrypoint (MongoDB)
# CMD ["--port 27017"]
CMD ["--port 27017", "--smallfiles"]

# Default port to execute the entrypoint (GUNICORN)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app"]
