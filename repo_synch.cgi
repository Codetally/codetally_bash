#!/bin/bash

TOKEN=$1
USERNAME=$2
REPO_URL=$3

REPOS=$(curl -H 'Authorization: token '"$TOKEN" $REPO_URL)
if [ ! -d "$USERNAME" ]; then
	mkdir -p $USERNAME
	echo "[" > "$USERNAME/repositories.json"
else
	exit 0
fi

while read fileline; do
	mkdir -p "$USERNAME/$fileline"
	description=$(echo "$REPOS" | ./jq '.[] | select(.name=="'$fileline'") | .description')
	id=$(echo "$REPOS" | ./jq -r '.[] | select(.name=="'$fileline'") | .id')
	html_url=$(echo "$REPOS" | ./jq -r '.[] | select(.name=="'$fileline'") | .html_url')
	author=$(echo "$REPOS" | ./jq -r '.[] | select(.name=="'$fileline'") | .owner.name')

	CURRENTJSON=$(cat <<EOT
	{
        	"title":"$fileline",
	        "description": $description,
        	"html_url":"$html_url",
	        "relative_url":"/$USERNAME/$fileline",
        	"branch":"na",
	        "message":"N/A",
        	"calculation_result":false,
	        "commit_id":"N/A",
        	"commit_url":"N/A",
	        "elapsed_time":"0",
        	"calculation_date":"N/A",
	        "author_name":"$author",
        	"committer_name":"N/A",
	        "calculation_value":"0.00",
        	"calculation_unit":"\$",
	        "calculation_currency":"CAD",
        	"repo_total_cost":"0.00"
	}
EOT
)
	echo "$CURRENTJSON," >> "$USERNAME/repositories.json"
	echo "$CURRENTJSON" > "$USERNAME/$fileline/current.json"

	CONFIG=$(cat << EOT
{
  "charges": [
    {
      "event": "commit",
      "action": "added",
      "chargetype": "author",
      "chargeref": "gemartin@gmail.com",
      "description": "This is an example of an author-specific charge for Greg when he adds something in a commit. Greg's commits make time travel possible, which is why the charge is a negative value (a negative charge is typically called a discount).",
      "calculationtype": "normal",
      "chargeamount": "-11.13",
      "currency": "CAD"
    }
  ]
}
EOT
)
	echo "$CONFIG" > "$USERNAME/$fileline/config.json"
	./logreset.cgi "$USERNAME" "$fileline"
	./log.cgi "$USERNAME" "$fileline" "When calculation of an event happens, each step is logged and will appear here." "INFO"
	./shield.cgi "0.00" > "./$USERNAME/$fileline/shield.svg"

done <<< "$(echo "$REPOS" | ./jq -r '.[] | .name')"

REPOFILE=$(<"$USERNAME/repositories.json")
CUTTED=${REPOFILE:0:${#REPOFILE} - 1}
echo "$CUTTED]" > "$USERNAME/repositories.json"

#echo "]" >> "$USERNAME/repositories.json"

exit 0
