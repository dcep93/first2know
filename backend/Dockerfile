FROM python:3.9-buster

# TODO dcep93 modal app from image from dockerfile
# RUN apt-get install -y software-properties-common
# RUN apt-add-repository non-free
# RUN apt-add-repository contrib
RUN apt-get update

RUN pip3 install  --upgrade pip

RUN pip3 install playwright==1.20.0
# RUN playwright install-deps chromium
RUN playwright install chromium

RUN apt install -y git
RUN pip3 install git+https://github.com/ozgur/python-firebase
RUN pip3 install cryptography
RUN pip3 install requests

RUN pip3 install uvicorn
RUN pip3 install fastapi

WORKDIR /var/www

EXPOSE 8000

COPY . ./

# CMD uvicorn first2know.server:web_app --host 127.0.0.1 --port 8000
