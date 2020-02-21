#!/bin/bash

TOKEN=$(./postvars.cgi $HTTP_COOKIE "X-AUTH-TOKEN=")
HTTP_CODE=$(curl -o /dev/null --silent --head --write-out '%{http_code}\n' -H 'Authorization: token '"$TOKEN" https://api.github.com/user)
if [ "$HTTP_CODE" -eq "200" ]; then
	USER=$(curl -H 'Authorization: token '"$TOKEN" https://api.github.com/user)
#synch repos
	USERNAME=$(echo "$USER" | ./jq '.["login"]'  -r)
	REPO_URL=$(echo "$USER" | ./jq '.["repos_url"]'  -r)
	./repo_synch.cgi "$TOKEN" "$USERNAME" "$REPO_URL"
	echo "Content-type: application/json"
	echo ""
	echo "$USER"
else
	echo "Status: 401 - $HTTP_CODE"
	echo ""
fi

exit 0


