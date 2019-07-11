#!/bin/bash

# GRANT pub,sub energise/lpbc/{lpbc_name}/*
# GRANT sub energise/spbc/*
# GRANT sub energise/upmu/*

if [ -z "$1" ]; then
    echo "Provide LPBC name (no spaces)"
    exit 1
fi

source environment.sh
source lib.sh

make_user_entity

lpbc_name=$1
LPBC_ENTITY="${lpbc_name}.ent"
create_entity "${lpbc_name}" $LPBC_ENTITY

# create dots

# publish as LPBC
echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/lpbc/${lpbc_name}/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $LPBC_ENTITY -e 3y --indirections 0 "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/lpbc/${lpbc_name}/*"
    echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/lpbc/${lpbc_name}/*"
    wv verify test.pem
else
    wv verify test.pem
fi

# subscribe to SPBC
echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/spbc/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $LPBC_ENTITY -e 3y --indirections 0 "wavemq:subscribe@${ENERGISE_NAMESPACE}/spbc/*"
    echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/spbc/*"
    wv verify test.pem
else
    wv verify test.pem
fi

# subscribe to upmu
echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $LPBC_ENTITY -e 3y --indirections 0 "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
    echo "\n" | wv rtprove --subject $LPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
    wv verify test.pem
else
    wv verify test.pem
fi
