#!/bin/bash

CODECOST=$(./postvars.cgi $QUERY_STRING "codecost=")
CODECOSTCODE=$(./postvars.cgi $QUERY_STRING "currency_code=")

FANCYAMOUNT=$(./fancy_currency.cgi "$CODECOST" "$CODECOSTCODE")

echo "Content-Type:image/svg+xml"
echo ""

RESULT=$(./shield.cgi "$FANCYAMOUNT")
echo "$RESULT"

exit 0
