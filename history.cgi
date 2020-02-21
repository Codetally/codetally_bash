#!/bin/bash

OWNER=$1
REPO=$2
CURRENTFILE="./$OWNER/$REPO/current.json"
CURRENTJSON=$(<"$CURRENTFILE")

# Step 1: look up or create the history directory.

HISTORYDIRECTORY="./$OWNER/$REPO/history"
if [ ! -d "$HISTORYDIRECTORY" ]; then
        mkdir -p "$HISTORYDIRECTORY"
fi

#Step 2: Save the current JSON into that directory. I am using the commit id, but may need to later adjust to sequence.

CURRENTID=$(echo "$CURRENTJSON" | ./jq -r '.commit_id')
NEXTHISTORYFILE="$HISTORYDIRECTORY/$CURRENTID.json"
echo "$CURRENTJSON" > $NEXTHISTORYFILE

#Step 3: Add the new entry to the history file. 

HISTORYFILE="./$OWNER/$REPO/history.json"
echo "{\"history\":[" > "$HISTORYFILE"

for filename in ./$OWNER/$REPO/history/*.json; do
	HISTORYENTRY=$(<"$filename")
	echo "$HISTORYENTRY," >> $HISTORYFILE
done

HISTORYDATA=$(<"$HISTORYFILE")
HISTORYDATA=${HISTORYDATA:0:${#HISTORYDATA} - 1}
echo "$HISTORYDATA]}" > $HISTORYFILE

exit 0
