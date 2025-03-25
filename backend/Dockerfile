FROM debian:11
# FROM debian:11@sha256:e538a2f0566efc44db21503277c7312a142f4d0dedc5d2886932b92626104bff

WORKDIR /var/www

# RUN apt-add-repository non-free
# RUN apt-add-repository contrib

RUN apt-get update

RUN apt-get install -y software-properties-common
RUN apt install -y curl git python-is-python3 python3.9 python3-pip

RUN pip3 install --upgrade pip

# for playwright
# solves: E: Package "ttf-ubuntu-font-family" has no installation candidate
RUN echo "deb http://ftp.us.debian.org/debian buster main non-free" >>/etc/apt/sources.list.d/fonts.list

RUN pip3 install playwright==1.36
RUN playwright install-deps chromium
RUN playwright install chromium

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . ./
