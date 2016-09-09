FROM debian:sid
MAINTAINER Boris Fritscher

# fix sid install
RUN set -x; \
    echo "deb http://httpredir.debian.org/debian jessie main" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -t jessie -y --no-install-recommends \
        libfreeradius-client2 \
    && apt-get install -y --no-install-recommends \
        asterisk \
        asterisk-mp3 \
        asterisk-espeak \
        asterisk-prompt-fr-armelle \
        asterisk-moh-opsound-wav \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/* \

CMD asterisk -fvvvvv