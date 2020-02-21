#!/bin/bash

OWNER=$1
REPO=$2
MESSAGE=$3
LEVEL=$4
TIMESTAMP=`date +%Y-%m-%d:%H:%M:%S`
LOGFILE="./$OWNER/$REPO/log.json"

LOGJSON="[{\"timestamp\":\"$TIMESTAMP\",\"message\":\"$MESSAGE\",\"level\":\"$LEVEL\"}]";

LOGDATA=$(<$LOGFILE)

CMD=".loglines += $LOGJSON"
LOGLINES=$(echo "$LOGDATA" | ./jq -r "$CMD")

echo "$LOGLINES" > "$LOGFILE"


exit 0

