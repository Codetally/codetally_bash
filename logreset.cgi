#!/bin/bash

OWNER=$1
REPO=$2
LOGFILE="./$OWNER/$REPO/log.json"
echo "{\"loglines\": []}" > "$LOGFILE"

exit 0

