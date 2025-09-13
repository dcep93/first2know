FROM debian:12

WORKDIR /var/www

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
COPY dockerbuild.sh ./
RUN bash dockerbuild.sh

COPY . ./
