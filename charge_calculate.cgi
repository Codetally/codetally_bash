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
./log.cgi "$OWNER" "$REPO" "Tax charge amount found of $taxcharge percent" "INFO"

TAXAMOUNT=$(echo "scale=2; $GRANDTOTAL * $taxcharge / 100" | bc )
./log.cgi "$OWNER" "$REPO" "The tax amount is: $TAXAMOUNT" "INFO"

./log.cgi "$OWNER" "$REPO" "Pre-tax calculation is: $GRANDTOTAL" "INFO"
GRANDTOTAL=$(echo "scale=2; $GRANDTOTAL + $TAXAMOUNT" | bc )
./log.cgi "$OWNER" "$REPO" "Post-tax calculation is: $GRANDTOTAL" "INFO"


done <<< "$(echo "$FILE" | ./jq -r '.["charges"][] | select(.chargetype == "tax") | .chargeamount')"

ENDTIME=$(($(date +%s%N)/1000000))

ELAPSEDTIME=$(($ENDTIME - $STARTTIME))
ELAPSEDTIME=$(echo "scale=3; $ELAPSEDTIME / 1000"  | bc )

./build_current.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "$GRANDTOTAL" "$CHARGECURRENCY" "$CURRENCYUNIT" "$ELAPSEDTIME" "$RESULT"
exit 0
