FROM ubuntu 
RUN apt-get update 
RUN apt install -y python3 && apt-get -y install python3-pip
WORKDIR /multilex 
COPY . /multilex/
RUN pip3 install -r requirements.txt
CMD [ "luigi","--module morning MorningPipeline "]