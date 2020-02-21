#!/bin/bash

AMOUNT=$1
CURRCODE=$2

if (( $( bc <<< "($AMOUNT > 999999999)" ) )); then
        AMOUNT=$(echo "scale=2; $AMOUNT / 1000000000"  | bc )
        AMOUNT="$AMOUNT B"
elif (( $( bc <<< "($AMOUNT > 999999)" ) )); then
        AMOUNT=$(echo "scale=2; $AMOUNT / 1000000"  | bc )
        AMOUNT="$AMOUNT M"
elif (( $( bc <<< "($AMOUNT > 999)" ) )); then
        AMOUNT=$(echo "scale=2; $AMOUNT / 1000"  | bc )
        AMOUNT="$AMOUNT K"
fi

CURRSYM=$(./fancy_symbol.cgi "$CURRCODE")

echo "$CURRSYM $AMOUNT"

exit 0
