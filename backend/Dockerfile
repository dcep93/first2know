FROM debian:11
# FROM debian:11@sha256:e538a2f0566efc44db21503277c7312a142f4d0dedc5d2886932b92626104bff

WORKDIR /var/www

# RUN apt-add-repository non-free
# RUN apt-add-repository contrib

RUN apt-get update
RUN apt-get install -y software-properties-common

RUN apt install -y python3.9
RUN apt install -y python3-pip

RUN pip3 install  --upgrade pip

RUN apt install python-is-python3
RUN apt install -y git

# for playwright
# solves: E: Package "ttf-ubuntu-font-family" has no installation candidate
RUN echo "deb http://ftp.us.debian.org/debian buster main non-free" >> /etc/apt/sources.list.d/fonts.list

# RUN pip3 install playwright==1.22
RUN pip3 install playwright==1.27
RUN playwright install-deps chromium
RUN playwright install chromium

RUN pip3 install pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install --system

# EXPOSE 8000

COPY . ./

# RUN mypy .
