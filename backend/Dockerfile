FROM debian:11

WORKDIR /var/www

# TODO dcep93 modal app from image from dockerfile


# RUN apt-add-repository non-free
# RUN apt-add-repository contrib


RUN apt-get update
RUN apt-get install -y software-properties-common

RUN apt install -y python3.9
RUN apt install -y python3-pip

RUN pip3 install  --upgrade pip

# for playwright
# solves: E: Package "ttf-ubuntu-font-family" has no installation candidate
RUN echo "deb http://ftp.us.debian.org/debian buster main non-free" >> /etc/apt/sources.list.d/fonts.list

RUN pip3 install playwright==1.20.0
RUN playwright install-deps chromium
RUN playwright install chromium

RUN apt install -y git
RUN pip3 install git+https://github.com/ozgur/python-firebase
RUN pip3 install cryptography
RUN pip3 install requests

RUN pip3 install uvicorn
RUN pip3 install fastapi

EXPOSE 8000

COPY . ./

# CMD uvicorn first2know.server:web_app --host 127.0.0.1 --port 8000
