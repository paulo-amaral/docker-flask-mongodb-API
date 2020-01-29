[![alt text][1.1]][1]
[![alt text][2.1]][2]
[![alt text][3.1]][3]

[1.1]: http://i.imgur.com/tXSoThF.png (twitter icon with padding)
[2.1]: http://i.imgur.com/P3YfQoD.png (facebook icon with padding)
[3.1]: http://i.imgur.com/0o48UoR.png (github icon with padding)


[1]: http://www.twitter.com/paulo_s_amaral
[2]: https://www.facebook.com/paulo.s.amaral
[3]: http://www.github.com/paulo-amaral


## DOCKER - FLASK/MONGODB API
Dev Environment - Python Flask App API with MongoDB using Docker Compose.


## Motivation
This deploy was used for a humanitarian project by (JUS/UNWOMEN). This project permits that some people reporting sexual harassment in the public service in TIMOR-LESTE. We have been created a chatbot called ROSA.This Chatbot receives the complaints via API and saves it into a mongodb database for CRUD operations.

Check ROSA bot : https://m.me/RosaCFP - Under development.


## Required Software
It uses Docker CE and Docker-compose: Compose is a tool for defining and running complex applications with Docker. With Compose, you define a multi-container application in a single file, then spin your application up in a single command which does everything that needs to be done to get it running.

### To install, use my personal script (CentOS/Debian/Ubuntu) like this:

https://github.com/paulo-amaral/Install-docker-ce-docker-compose

### Hands-on Install
Install Docker CE:

https://do.co/2TVqbbH

Install Docker-compose :

https://docs.docker.com/compose/install/

After installing Docker and Docker-compose on your machine, you can go to the project main folder and type:

$docker-composer build

$docker-compose up

Docker-compose will build the containers necessary for your environment. Basically there will be two containers, one with Python, Flask and a few modules and another container with MongoDB bound to the first. The environment structure is as follow:


## How to install
   ## 1 - Clone repo:
     git clone https://github.com/paulo-amaral/docker-flask-mongodb-API.git
     
   ## 2 - Build : (optional) 
     $docker-compose build
     
   ## 3 - Start and debug:
     $docker-compose up
     
## Start NGROK and API(optional)
After deploy, you can use or setup a NGROK - https://ngrok.com/

This handy tool lets you set up a secure tunnel to your localhost, which is a fancy way of saying it opens access to your local API from the internet:

`
$./ngrok http 8080
`   
