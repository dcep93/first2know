FROM debian:12

WORKDIR /var/www

RUN apt-get update

RUN apt install -y curl git python-is-python3 python3-pip python3.11-venv

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

RUN pip install playwright==1.53.0
RUN playwright install --with-deps chromium

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
