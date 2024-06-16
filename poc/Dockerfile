# FROM debian:11
FROM debian:11@sha256:d584e02c85bc9b3bd8df01662e4f605a66e1b9a04f9dea0e288f56da474269a0

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
RUN pip3 install gunicorn
RUN pip3 install flask

COPY . ./

ENTRYPOINT [ "gunicorn", "-b", ":8080", "main:app" ]
