#!/bin/bash

source lib.sh

check_var ENERGISE_NAMESPACE
check_var ENERGISE_GRANTER_ENTITY
check_var ENERGISE_SITE_ROUTER_ENTITY
check_var ENERGISE_LPBC_ENTITY
check_var ENERGISE_SPBC_ENTITY
check_var ENERGISE_USER_ENTITY

curdir=$(pwd)

$echo "${INFO}Getting latest containers${NC}"
docker pull xbos/waved:latest
docker pull xbos/wavemq:latest


$echo "${INFO}Setting up WAVED, WAVEMQ${NC}"
setup_waved

$echo "${INFO}Creating entities${NC}"
create_entity "ENERGISE_LPBC_ENTITY" $ENERGISE_LPBC_ENTITY
create_entity "ENERGISE_SPBC_ENTITY" $ENERGISE_SPBC_ENTITY
create_entity "ENERGISE_USER_ENTITY" $ENERGISE_USER_ENTITY
create_entity "ENERGISE_SITE_ROUTER_ENTITY" $ENERGISE_SITE_ROUTER_ENTITY

$echo "${INFO}Granting permissions${NC}"
# create dots
echo "\n" | wv rtprove --subject $ENERGISE_USER_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_GRANTER_ENTITY --subject $ENERGISE_USER_ENTITY -e 3y --indirections 5 "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/*"
    echo "\n" | wv rtprove --subject $ENERGISE_USER_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/*"
    wv verify test.pem
else
    wv verify test.pem
fi

$echo "${INFO}Setting up WAVEMQ, Ingester${NC}"
setup_wavemq
