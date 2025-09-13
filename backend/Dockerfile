FROM debian:12

WORKDIR /var/www

ENV PATH="/opt/venv/bin:$PATH"

COPY dockerbuild.sh requirements.txt ./
RUN bash dockerbuild.sh

COPY . ./
