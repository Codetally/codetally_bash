#!/bin/bash

if [ -z "$1" ]; then
        exit 0
else
	ENCODED_DATA=$1
	url_encoded="${ENCODED_DATA//+/ }"
	POST_DATA=$(printf '%b' "${url_encoded//%/\\x}")

        XX=`echo "$POST_DATA" | sed -n 's/^.*'"$2"'\([^&]*\).*$/\1/p' | sed "s/%20/ /g"`
        echo $XX
fi
exit 0
