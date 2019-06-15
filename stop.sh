#!/bin/bash

container_running() {
    docker inspect $1 | jq -e ".[0].State.Running" >/dev/null 2>&1
}

container_exists() {
    docker inspect $1 >/dev/null 2>&1
}

for container in energise-wavemq energise-waved; do
    if container_running $container ; then
        echo "Killing $container"
    docker kill $container
    fi
    if container_exists $container ; then
        echo "Removing $container"
    docker rm $container
    fi
done
