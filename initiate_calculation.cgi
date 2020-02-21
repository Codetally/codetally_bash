#!/bin/bash

OWNER=$1
REPO=$2
GITHUB_EVENT=$3
HEADCOMMITID=$4
POST_DATA=$5
SETVALUES=$6

CLIENTID="5618700d534bdfd9610b"
CLIENTSECRET="117c8e057ff0d8c31f6ff5155c149d26def8e2fc"

CLIENT_SUFFIX="client_id=$CLIENTID&client_secret=$CLIENTSECRET"


RAWDIRECTORY="./$OWNER/$REPO/raw_events"
if [ ! -d "$RAWDIRECTORY" ]; then
        mkdir -p "$RAWDIRECTORY"
fi
EVENTDIRECTORY="$RAWDIRECTORY/$GITHUB_EVENT"
if [ ! -d "$EVENTDIRECTORY" ]; then
        mkdir -p "$EVENTDIRECTORY"
fi

if [ "$SETVALUES" = "TRUE" ]; then
	echo "$POST_DATA" > $EVENTDIRECTORY/$HEADCOMMITID.json

	FILENAME="codecost.json"
	CHARGES_URL="https://api.github.com/repos/$OWNER/$REPO/contents/$FILENAME"
	MEDIATYPE="application/vnd.github.VERSION.raw"
	FILE=$(curl "$CHARGES_URL?$CLIENT_SUFFIX" -H "Accept: $MEDIATYPE")

	echo "$FILE" > ./$OWNER/$REPO/config.json
fi

./logreset.cgi "$OWNER" "$REPO"

#was there a timelog.json file included in the checkin? If so, use that instead (timelogging overrides).
ISTIMELOG=true

TIMELOG=$(echo "$FILE" | ./jq -r  '.["commits"][].added[] | select(.=="timelog.json")'  2> /dev/null)

if [ -z "$TIMELOG" ]; then
	ISTIMELOG=$(echo "$FILE" | ./jq -r  '.["commits"][].modified[] | select(.=="timelog.json")' 2> /dev/null)
	if [ -z "$TIMELOG" ]; then
		ISTIMELOG=false
	fi
fi

echo "$ISTIMELOG"
exit 0
