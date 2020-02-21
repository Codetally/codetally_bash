#!/bin/bash

OWNER=$1
REPO=$2
GITHUB_EVENT=$3
HEADCOMMITID=$4

STARTTIME=$(($(date +%s%N)/1000000))

RESULT=false

POST_DATA=$(<"./$OWNER/$REPO/raw_events/$GITHUB_EVENT/$HEADCOMMITID.json")

REPODESC=$(echo "$POST_DATA" | ./jq '.["repository"]["description"]'  -r)
REPOURL=$(echo "$POST_DATA" | ./jq '.["repository"]["html_url"]'  -r)
REPORELATIVE=$(echo "$POST_DATA" | ./jq '.["repository"]["full_name"]'  -r)

FILENAME="codecost.json"
CHARGES_URL="https://api.github.com/repos/$OWNER/$REPO/contents/$FILENAME"
MEDIATYPE="application/vnd.github.VERSION.raw"
FILE=$(curl $CHARGES_URL -H "Accept: $MEDIATYPE")

echo "$FILE" > ./$OWNER/$REPO/config.json

./logreset.cgi "$OWNER" "$REPO"

CURRENCYUNIT="DOLLARS"

CHARGECURRENCY=$(echo "$FILE" | ./jq -r  '.currency')
if [ -n "$CHARGECURRENCY" ]; then
	./log.cgi "$OWNER" "$REPO" "The currency found was: $CHARGECURRENCY" "INFO"
else
	./log.cgi "$OWNER" "$REPO" "No currency was found. Defaulting to CAD" "WARN"
	CHARGECURRENCY="CAD"
fi

#was there a timelog.json file included in the checkin? If so, use that instead (timelogging overrides).
ISTIMELOG=true

TIMELOG=$(echo "$FILE" | ./jq -r  '.["commits"][].added[] | select(.=="timelog.json")'  2> /dev/null)

if [ -z "$TIMELOG" ]; then
	ISTIMELOG=$(echo "$FILE" | ./jq -r  '.["commits"][].modified[] | select(.=="timelog.json")' 2> /dev/null)
	if [ -z "$TIMELOG" ]; then
		ISTIMELOG=false
	fi
fi


if [ "$ISTIMELOG" = true ]; then
	HEADCOMMITAUTHOREMAIL=$(echo "$POST_DATA" | ./jq -r '.head_commit.author.email')
	AUTHORRATE=$(echo "$FILE" | ./jq -r  '.["hourly_rates"] [] | select(.author_email =="'$HEADCOMMITAUTHOREMAIL'") | .cost_per_hour')
	if [ -z "$AUTHORRATE" ]; then
		#A timelog was added, but the commit author either was not found, or the rate was not found.
	        ./log.cgi "$OWNER" "$REPO" "ERROR: No hourly rate found for commit author: $HEADCOMMITAUTHOREMAIL" "ERROR"
		#This is a "cannot proceed" type of error
		exit 0
	fi
	TIMELOGFILE="timelog.json"
	TIMELOG_URL="https://api.github.com/repos/$OWNER/$REPO/contents/$TIMELOGFILE"
	MEDIATYPE="application/vnd.github.VERSION.raw"
	TIMEFILE=$(curl $TIMELOG_URL -H "Accept: $MEDIATYPE")
	if [ -z "$TIMEFILE" ]; then
		#Somehow no timelog was found?
	        ./log.cgi "$OWNER" "$REPO" "ERROR: No timelog.json was found at the root level of the repo $REPO." "ERROR"
		#This is another "cannot proceed" type of error
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
fi

TOTALAMOUNT=0
count=0

while read line; do
        ./log.cgi "$OWNER" "$REPO" "Processing a commit for author: $line" "INFO"
        logtimestamp=$(echo "$POST_DATA" | ./jq -r '.["commits"]['"$count"'].timestamp')
        ./log.cgi "$OWNER" "$REPO" "The timestamp for commit #$count is $logtimestamp" "INFO"

        while read fileline; do
                if [ -n "$fileline" ]; then
                        ./log.cgi "$OWNER" "$REPO" "An added record was found: $fileline" "INFO"
			AUTHORAMOUNT=$(echo "$FILE" | ./jq -r  '.["charges"] [] | select(.event =="commit") | select(.action == "added") | select(.chargetype == "author") | select(.chargeref == "'$line'") | .chargeamount')
                        if [ -n "$AUTHORAMOUNT" ]; then
                               	./log.cgi "$OWNER" "$REPO" "Action: added; Chargetype: author; Amount: $AUTHORAMOUNT; Chargeref: $fileline" "INFO"
				RESULT=true
                        else
                            	AUTHORAMOUNT="0"
                                ./log.cgi "$OWNER" "$REPO" "Action: added; Chargetype: author; Amount: $AUTHORAMOUNT; Chargeref: $fileline; Message: No Charge found." "INFO"
                       	fi
                        TOTALAMOUNT="$TOTALAMOUNT + ($AUTHORAMOUNT)"
                fi
        done <<< "$(echo "$POST_DATA" | ./jq -r '.["commits"]['"$count"'] | .added[] | @uri')"
        while read fileline; do
                if [ -n "$fileline" ]; then
                        ./log.cgi "$OWNER" "$REPO" "A modified record was found: $fileline" "INFO"
			AUTHORAMOUNT=$(echo "$FILE" | ./jq -r  '.["charges"] [] | select(.event =="commit") | select(.action == "modified") | select(.chargetype == "author") | select(.chargeref == "'$line'") | .chargeamount')
                        if [ -n "$AUTHORAMOUNT" ]; then
                                ./log.cgi "$OWNER" "$REPO" "AUTHORAMOUNT found for $fileline: $AUTHORAMOUNT" "INFO"
				RESULT=true
                        else
                            	AUTHORAMOUNT="0"
                                ./log.cgi "$OWNER" "$REPO" "AUTHORAMOUNT not found for $fileline", "WARN"
                        fi
                        TOTALAMOUNT="$TOTALAMOUNT + ($AUTHORAMOUNT)"
                fi
         done <<< "$(echo "$POST_DATA" | ./jq -r '.["commits"]['"$count"'] | .modified[] | @uri')"
         while read fileline; do
                if [ -n "$fileline" ]; then
                        ./log.cgi "$OWNER" "$REPO" "A removed record was found: $fileline" "INFO"
			AUTHORAMOUNT=$(echo "$FILE" | ./jq -r  '.["charges"] [] | select(.event =="commit") | select(.action == "removed") | select(.chargetype == "author") | select(.chargeref == "'$line'") | .chargeamount')
                        if [ -n "$AUTHORAMOUNT" ]; then
                            	./log.cgi "$OWNER" "$REPO" "AUTHORAMOUNT found for $fileline: $AUTHORAMOUNT" "INFO"
				RESULT=true
                        else
                               	AUTHORAMOUNT="0"
                                ./log.cgi "$OWNER" "$REPO" "AUTHORAMOUNT not found for $fileline", "WARN"
                        fi
                       	TOTALAMOUNT="$TOTALAMOUNT + ($AUTHORAMOUNT)"
                fi
         done <<< "$(echo "$POST_DATA" | ./jq -r '.["commits"]['"$count"'] | .removed[] | @uri')"

(( count++ ))
done <<< "$(echo "$POST_DATA" | ./jq -r '.["commits"][].author.email')"

GRANDTOTAL=$(echo $TOTALAMOUNT | bc)
./log.cgi "$OWNER" "$REPO" "The list of individual charges is : $TOTALAMOUNT" "INFO"
./log.cgi "$OWNER" "$REPO" "The total amount is: $GRANDTOTAL" "INFO"

while read taxcharge; do

GRANDTOTAL=$(echo "scale=2; $GRANDTOTAL * $taxcharge / 100" | bc )

done <<< "$(echo "$FILE" | ./jq -r '.["charges"][] | select(.chargetype == "tax") | .chargeamount')"

ENDTIME=$(($(date +%s%N)/1000000))

ELAPSEDTIME=$(($ENDTIME - $STARTTIME))
ELAPSEDTIME=$(echo "scale=3; $ELAPSEDTIME / 1000"  | bc )

./build_current.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "$GRANDTOTAL" "$CHARGECURRENCY" "$CURRENCYUNIT" "$ELAPSEDTIME" "$RESULT"
exit 0
