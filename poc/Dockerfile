FROM debian:11
# FROM debian:11@sha256:e538a2f0566efc44db21503277c7312a142f4d0dedc5d2886932b92626104bff

WORKDIR /var/www

# RUN apt-add-repository non-free
# RUN apt-add-repository contrib

RUN apt-get update
RUN apt-get install -y software-properties-common

RUN apt install -y python3.9
RUN apt install -y python3-pip

RUN pip3 install --upgrade pip

RUN apt install python-is-python3

RUN apt install -y git

RUN pip3 install uvicorn
RUN pip3 install fastapi
