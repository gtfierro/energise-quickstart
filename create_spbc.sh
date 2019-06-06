#!/bin/bash

if [ -z "$1" ]; then
    echo "Provide SPBC name (no spaces)"
    exit 1
fi

source lib.sh

spbcname=$1
SPBC_ENTITY="${spbcname}.ent"
create_entity "${spbcname}" $SPBC_ENTITY
$echo "${INFO}Granting permissions${NC}"

# create dots

# publish as SPBC
echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/spbc/${spbcname}"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $SPBC_ENTITY -e 3y --indirections 0 "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/spbc/${spbcname}"
    echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:publish,subscribe@${ENERGISE_NAMESPACE}/spbc/${spbcname}"
    wv verify test.pem
else
    wv verify test.pem
fi

# subscribe to LPBC
echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/lpbc/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $SPBC_ENTITY -e 3y --indirections 0 "wavemq:subscribe@${ENERGISE_NAMESPACE}/lpbc/*"
    echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/lpbc/*"
    wv verify test.pem
else
    wv verify test.pem
fi

# subscribe to upmu
echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
if [[ $? != 0 ]]; then
    echo "\n" | wv rtgrant --attester $ENERGISE_USER_ENTITY --subject $SPBC_ENTITY -e 3y --indirections 0 "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
    echo "\n" | wv rtprove --subject $SPBC_ENTITY -o test.pem "wavemq:subscribe@${ENERGISE_NAMESPACE}/upmu/*"
    wv verify test.pem
else
    wv verify test.pem
fi

