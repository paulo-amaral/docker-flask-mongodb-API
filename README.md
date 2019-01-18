# DOCKER - FLASK/MONGODB API
Dev Environment - Python Flask App API with MongoDB using Docker Compose.

# Motivation
This deploy was used for a humanitarian project by (UNWOMEN), about reporting sexual harassment in the public service in TIMOR-LESTE country, where we created a chatbot called ROSA.This Chatbot receives the complaints and saves it to a mongobd database for CRUD operations.

Check ROSA bot : https://m.me/RosaCFP
Special thanks 

# Required Software
It uses Docker-compose: Compose is a tool for defining and running complex applications with Docker. With Compose, you define a multi-container application in a single file, then spin your application up in a single command which does everything that needs to be done to get it running.

https://docs.docker.com/compose/install/

After installing Docker and Docker-compose on your machine, you can go to the project main folder and type:

$docker-composer build

$docker-compose up

Docker-compose will build the containers necessary for your environment. Basically there will be two containers, one with Python, Flask and a few modules and another container with MongoDB bound to the first. The environment structure is as follow:
Frontend - Python/flask
Mongodb - Database to save complaints

# Howto install
   # 1 - Clone repo:
     git clone https://github.com/paulo-amaral/docker-flask-mongodb-API.git
   # 2 - Build :
     $docker-composer build
   # 3 - Start and debug:
     $docker-composer up
    
    
