#!/bin/bash

if [ -z "$1" ]; then
    echo "Provide LPBC name (no spaces)"
    exit 1
fi

source lib.sh

lpbcname=$1
LPBC_ENTITY="${lpbcname}.ent"
create_entity "${lpbc_name}" $LPBC_ENTITY
$echo "${INFO}Granting permissions${NC}"

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
