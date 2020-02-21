#!/bin/bash

OWNER=$1
REPO=$2
GITHUB_EVENT=$3
HEADCOMMITID=$4
GRANDTOTAL=$5
CHARGECURRENCY=$6
CURRENCYUNIT=$7
ELAPSEDTIME=$8
CALCULATIONRESULT=$9

POST_DATA=$(<"./$OWNER/$REPO/raw_events/$GITHUB_EVENT/$HEADCOMMITID.json")

REPODESC=$(echo "$POST_DATA" | ./jq '.["repository"]["description"]'  )
REPOURL=$(echo "$POST_DATA" | ./jq '.["repository"]["html_url"]'  -r)
REPORELATIVE=$(echo "$POST_DATA" | ./jq '.["repository"]["full_name"]'  -r)
HEADCOMMITMESSAGE=$(echo "$POST_DATA" | ./jq '.head_commit.message')
HEADCOMMITTIMESTAMP=$(echo "$POST_DATA" | ./jq -r '.head_commit.timestamp')
HEADCOMMITURL=$(echo "$POST_DATA" | ./jq -r '.head_commit.url')
HEADCOMMITID=$(echo "$POST_DATA" | ./jq -r '.head_commit.id')
HEADCOMMITAUTHOR=$(echo "$POST_DATA" | ./jq -r '.head_commit.author.name')
HEADCOMMITCOMMITTER=$(echo "$POST_DATA" | ./jq -r '.head_commit.committer.name')

CALCULATIONDATE=`date +%Y-%m-%dT%H:%M:%S`

CURRENTFILE="./$OWNER/$REPO/current.json"
CURRENTCONTENT=""

if [ -f "$CURRENTFILE" ]; then
	CURRENTCONTENT=$(<"$CURRENTFILE")
fi
REPOTOTALCOST=$(echo "$CURRENTCONTENT" | ./jq -r '.repo_total_cost')
if [ -z "$REPOTOTALCOST" ]; then
        REPOTOTALCOST=0
fi

REVISEDREPOTOTALCOST=$(echo "scale=2; $REPOTOTALCOST + $GRANDTOTAL"  | bc )

CURRENTJSON=$(cat <<EOT
{
        "title":"$REPO",
        "description": $REPODESC,
        "html_url":"$REPOURL",
        "relative_url":"/$REPORELATIVE",
        "message": $HEADCOMMITMESSAGE,
        "calculation_result":$CALCULATIONRESULT,
        "commit_id":"$HEADCOMMITID",
        "commit_url":"$HEADCOMMITURL",
        "elapsed_time":"$ELAPSEDTIME",
        "calculation_date":"$CALCULATIONDATE",
        "author_name":"$HEADCOMMITAUTHOR",
        "committer_name":"$HEADCOMMITCOMMITTER",
        "calculation_value":"$GRANDTOTAL",
        "calculation_unit":"$CURRENCYUNIT",
        "calculation_currency":"$CHARGECURRENCY",
        "repo_total_cost":"$REVISEDREPOTOTALCOST"
}
EOT
)
echo "$CURRENTJSON" > $CURRENTFILE

exit 0
