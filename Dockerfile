
FROM mongo:latest
LABEL maintainer="Paulo Amaral - paulo.security@gmail.com"

FROM python:3.7
ADD . /rosa_crud
WORKDIR /opt/projetos/dev/rosa_crud
RUN apt-get update
RUN apt-get install -y python3-setuptools nano 
RUN apt-get install -y python3-pip
RUN pip3 install flask
RUN pip3 install pymongo 
RUN pip3 install flask-restful
RUN pip3 install requests
RUN pip3 install -U flask-cors

# Expose the default port
EXPOSE 27017

# Default port to execute the entrypoint (MongoDB)
# CMD ["--port 27017"]
CMD ["--port 27017", "--smallfiles"]
