FROM debian:11

WORKDIR /var/www

# TODO akshat modal app from image from dockerfile


# RUN apt-add-repository non-free
# RUN apt-add-repository contrib


RUN apt-get update
RUN apt-get install -y software-properties-common

RUN apt install -y python3.9
RUN apt install -y python3-pip

RUN pip3 install  --upgrade pip

RUN apt install -y git
RUN pip3 install grpcio==1.43.0
RUN pip3 install cryptography
RUN pip3 install requests

RUN pip3 install uvicorn
RUN pip3 install fastapi
RUN pip3 install requests_oauthlib

# for playwright
# solves: E: Package "ttf-ubuntu-font-family" has no installation candidate
RUN echo "deb http://ftp.us.debian.org/debian buster main non-free" >> /etc/apt/sources.list.d/fonts.list

RUN pip3 install playwright==1.22
RUN playwright install-deps chromium
RUN playwright install chromium

RUN pip3 install git+https://github.com/ozgur/python-firebase

EXPOSE 8000

COPY . ./
