FROM ubuntu 
RUN apt-get update 
RUN apt-get get install python3.8
WORKDIR /multilex 
COPY . /multilex/
