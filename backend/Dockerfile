FROM debian:12

WORKDIR /var/www

ENV PATH="/opt/venv/bin:$PATH"

COPY dockerbuild.sh ./
RUN dockerbuild.sh

COPY . ./
