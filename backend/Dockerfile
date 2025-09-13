FROM debian:12

WORKDIR /var/www

ENV PATH="/opt/venv/bin:$PATH"

COPY dockerbuild.sh ./
RUN bash dockerbuild.sh

COPY . ./
