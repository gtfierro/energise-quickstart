#!/bin/bash

command_exists() {
    command -v "$@" > /dev/null 2>&1
}

if ! command_exists wv; then
    echo "Install docker"
    exit 1
fi

if ! command_exists docker; then
    echo "Install docker"
    exit 1
fi


function check_var() {
    if [[ "${!1}" == "" ]]
    then
        echo "Please set \$$1"
        echo "May need to source environment.sh"
        exit 1
    fi
}

echo='echo -e'
RED='\033[1;31m'
BLUE='\033[1;34m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
INFO=$YELLOW
PROMPT=$BLUE
ERROR=$RED
OK=$GREEN
NC='\033[0m' # No Color

function setup_waved() {
    # set up waved
    docker kill energise-waved
    docker rm energise-waved
    OPUT=$(docker run -d --name energise-waved \
                -v ${curdir}/etc/waved/:/etc/waved/ \
                -p 910:910 \
                --restart always \
                xbos/waved:latest 2>&1)
    echo $OPUT
    sleep 2
}

function create_entity() {
    entityname=$1
    filename=$2
    # create entities
    if [ ! -f ${filename} ]; then
        echo "Creating $entityname"
        wv mke -o $filename -e 10y --nopassphrase
        if [[ $? != 0 ]]
        then
            echo "Could not create $entityname ${filename}"
            exit 1
        fi
    fi
}

function setup_wavemq() {
    #cp energise-routeproof.pem etc/wavemq/.
    cp $ENERGISE_SITE_ROUTER_ENTITY etc/wavemq/.


    docker kill energise-wavemq
    docker rm energise-wavemq

    OPUT=$(docker run -d --name energise-wavemq \
                -v ${curdir}/etc/wavemq/:/etc/wavemq/ \
                -p 9516:4516 \
                --restart always \
                xbos/wavemq:latest 2>&1)
    echo $OPUT
}
