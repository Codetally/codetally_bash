#!/bin/bash

OWNER=$1
REPO=$2
GITHUB_EVENT=$3
HEADCOMMITID=$4

STARTTIME=$(($(date +%s%N)/1000000))

RESULT=false

POST_DATA=$(<"./$OWNER/$REPO/raw_events/$GITHUB_EVENT/$HEADCOMMITID.json")
FILE=$(<"./$OWNER/$REPO/config.json")

CHARGECURRENCY=$(echo "$FILE" | ./jq -r  '.currency')
if [ -n "$CHARGECURRENCY" ]; then
	./log.cgi "$OWNER" "$REPO" "The currency found was: $CHARGECURRENCY" "INFO"
else
	./log.cgi "$OWNER" "$REPO" "No currency was found. Defaulting to CAD" "WARN"
	CHARGECURRENCY="CAD"
fi

CURRENCYUNIT=$(./fancy_symbol.cgi "$CHARGECURRENCY")
if [ -n "$CURRENCYUNIT" ]; then
	./log.cgi "$OWNER" "$REPO" "The currency unit symbol found was: $CURRENCYUNIT" "INFO"
else
	./log.cgi "$OWNER" "$REPO" "No currency unit symbol was found. Defaulting to \$" "WARN"
	CURRENCYUNIT="\$"
fi

HEADCOMMITAUTHOREMAIL=$(echo "$POST_DATA" | ./jq -r '.head_commit.author.email')
AUTHORRATE=$(echo "$FILE" | ./jq -r  '.["hourly_rates"] [] | select(.author_email =="'$HEADCOMMITAUTHOREMAIL'") | .cost_per_hour')
if [ -z "$AUTHORRATE" ]; then
	#A timelog was added, but the commit author either was not found, or the rate was not found.
        ./log.cgi "$OWNER" "$REPO" "ERROR: No hourly rate found for commit author: $HEADCOMMITAUTHOREMAIL" "ERROR"
	./build_current.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "0" "$CHARGECURRENCY" "$CURRENCYUNIT" "0" "$RESULT"
	exit 0
fi
TIMELOGFILE="timelog.json"
TIMELOG_URL="https://api.github.com/repos/$OWNER/$REPO/contents/$TIMELOGFILE"
MEDIATYPE="application/vnd.github.VERSION.raw"
TIMEFILE=$(curl $TIMELOG_URL -H "Accept: $MEDIATYPE")
if [ -z "$TIMEFILE" ]; then
	#Somehow no timelog was found?
        ./log.cgi "$OWNER" "$REPO" "ERROR: No timelog.json was found at the root level of the repo $REPO." "ERROR"
	./build_current.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "0" "$CHARGECURRENCY" "$CURRENCYUNIT" "0" "$RESULT"
	exit 0
fi
TIMELOG_HOURS=$(echo "$TIMEFILE" | ./jq -r  '.time_worked[].hours')
TIMELOG_MINUTES=$(echo "$TIMEFILE" | ./jq -r  '.time_worked[].minutes')
TIMELOG_SECONDS=$(echo "$TIMEFILE" | ./jq -r  '.time_worked[].seconds')

#TODO: Support a setting to round up or down to the nearest hour
MINUTESASHOURS = "$TIMELOG_MINUTES" / 60 | bc;
SECONDSASHOURS = "$TIMELOG_SECONDS" / 60 / 60 | bc;
TOTALHOURS = "$TIMELOG_HOURS + $TIMELOGMINUTES + $TIMELOG_SECONDS | bc"
GRANDTOTAL_TIMELOG="$AUTHORRATE * $TOTALHOURS | bc"

ENDTIME_TIMELOG=$(($(date +%s%N)/1000000))

ELAPSEDTIME_TIMELOG=$(($ENDTIME_TIMELOG - $STARTTIME))
ELAPSEDTIME_TIMELOG=$(echo "scale=3; $ELAPSEDTIME_TIMELOG / 1000"  | bc )

RESULT=true

./build_current.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "$GRANDTOTAL_TIMELOG" "$CHARGECURRENCY" "$CURRENCYUNIT" "$ELAPSEDTIME_TIMELOG" "$RESULT"
exit 0

