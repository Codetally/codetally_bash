#!/bin/bash

GITHUB_EVENT="push"
OWNER=$1
REPO=$2
HEADCOMMITID=$3
POST_DATA=$4

#someday support "fromdate"...but not I see this will impact current.json.

echo "starting controller..."
echo "Own: $OWNER"
echo "Repo: $REPO"
echo "Comm: $HEADCOMMITID"

ISTIMELOG=$(./initiate_calculation.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID" "$POST_DATA" "FALSE")
echo "done timelog"

if [ "$ISTIMELOG" = "true" ]; then
	./timelog_calculate.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID"
else
	#TODO: authorcharge_calculate, foldercharge_calculate, taxcharge_calculate, adjustmentcharge_calculate (the cost is out of whack, and I need to whack it)
	#TODO: resetcharge_calculate (everything is pooched. reset to 0
	./charge_calculate.cgi "$OWNER" "$REPO" "$GITHUB_EVENT" "$HEADCOMMITID"
echo "finished controller"
fi

./history.cgi "$OWNER" "$REPO"
echo "finished history"

CURRENTFILE="./$OWNER/$REPO/current.json"
CURRENTJSON=$(<"$CURRENTFILE")
SHIELDCOST=$(echo "$CURRENTJSON" | ./jq -r '.repo_total_cost')
SHIELDCURRENCY=$(echo "$CURRENTJSON" | ./jq -r '.calculation_currency')

FANCYAMOUNT=$(./fancy_currency.cgi "$SHIELDCOST" "$SHIELDCURRENCY")
./shield.cgi "$FANCYAMOUNT" > "./$OWNER/$REPO/shield.svg"


echo "Status: 200"
echo ""

exit 0
