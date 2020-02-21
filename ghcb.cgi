#!/bin/bash

CODE=$(./postvars.cgi $QUERY_STRING "code=")

CLIENTID="5618700d534bdfd9610b"
CLIENTSECRET="117c8e057ff0d8c31f6ff5155c149d26def8e2fc"

RESPONSE=$(curl --data "client_id=$CLIENTID&client_secret=$CLIENTSECRET&code=$CODE" https://github.com/login/oauth/access_token)
TOKEN=$(./postvars.cgi $RESPONSE "access_token=")

TARGET_DATE=$(date --date '+20 min' -R -u)
echo "Set-Cookie: X-AUTH-TOKEN=$TOKEN; path=/; expires=$TARGET_DATE"
echo "Location: /index.html"
echo "Status: 302"
echo ""

exit 0
