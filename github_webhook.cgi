#!/bin/bash

STARTTIME=$(($(date +%s%N)/1000000))

POST_DATA=$(cat)

GITHUB_EVENT=$HTTP_X_GITHUB_EVENT
REPO=$(echo "$POST_DATA" | ./jq '.["repository"]["name"]'  -r)
OWNER=$(echo "$POST_DATA" | ./jq '.["repository"].owner.name'  -r)
HEADCOMMITID=$(echo "$POST_DATA" | ./jq -r '.head_commit.id')

ISTIMELOG=$(./initiate_calculation.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "$POST_DATA" "TRUE")
if [ "$ISTIMELOG" = "true" ]; then
	./timelog_calculate.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID"
else
	#TODO: authorcharge_calculate, foldercharge_calculate, taxcharge_calculate, adjustmentcharge_calculate (the cost is out of whack, and I need to whack it)
	#TODO: resetcharge_calculate (everything is pooched. reset to 0)
	./charge_calculate.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID"
fi
./history.cgi "$OWNER" "$REPO"

CURRENTFILE="./$OWNER/$REPO/current.json"
CURRENTJSON=$(<"$CURRENTFILE")
SHIELDCOST=$(echo "$CURRENTJSON" | ./jq -r '.repo_total_cost')
SHIELDCURRENCY=$(echo "$CURRENTJSON" | ./jq -r '.calculation_currency')

FANCYAMOUNT=$(./fancy_currency.cgi "$SHIELDCOST" "$SHIELDCURRENCY")
./shield.cgi "$FANCYAMOUNT" > "./$OWNER/$REPO/shield.svg"

echo "Status: 200"
echo ""

exit 0
