FROM ubuntu:18.04

RUN set -ex \
    && RUN_DEPS=" \
    wget \
    cdo \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libaec-dev \
    libcurl4-openssl-dev \
    curl \
    zip \
    unzip \
    bzip2 \
    gfortran \
    gcc \
    g++ \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && wget ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz \
    && tar -xzvf wgrib2.tgz \
    && cd grib2 \
    && export CC=gcc \
    && make \
    && cd wgrib2 \
    && cp wgrib2 /usr/local/bin \
    && rm -rf ~/* \
    \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*
