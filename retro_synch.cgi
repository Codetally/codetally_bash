#!/bin/bash

#OK, it sounds like the goal is:
# 1. get all the commits for a repo
# 2. for each commit, run the calc - produce history, etc

OWNER=$1
REPO=$2

CLIENTID="5618700d534bdfd9610b"
CLIENTSECRET="117c8e057ff0d8c31f6ff5155c149d26def8e2fc"

CLIENT_SUFFIX="client_id=$CLIENTID&client_secret=$CLIENTSECRET"

COMMITS_URL="https://api.github.com/repos/$OWNER/$REPO/commits"
COMMITS=$(curl "$COMMITS_URL?$CLIENT_SUFFIX")

while read fileline; do

	COMMIT_URL="$COMMITS_URL/$fileline"
	COMMIT=$(curl "$COMMIT_URL?$CLIENT_SUFFIX")

	AUTHOR_NAME="$(echo "$COMMIT" | ./jq -r '.commit.author.name')"
	AUTHOR_EMAIL="$(echo "$COMMIT" | ./jq -r '.commit.author.email')"
	TIMESTAMP="$(echo "$COMMIT" | ./jq -r '.commit.author.date')"
	MESSAGE="$(echo "$COMMIT" | ./jq '.commit.message')"

	ADDED=""
	MODIFIED=""
	REMOVED=""

	while read adds; do
		if [ -n "$adds" ]; then
			if [ -z "$ADDED" ]; then
				ADDED="\"$adds\""
			else
				ADDED="$ADDED,\"$adds\""
			fi
		fi
	done <<< "$(echo "$COMMIT" | ./jq -r '.files[] | select (.status == "added") | .filename')"
	while read mods; do
		if [ -n "$mods" ]; then
			if [ -z "$MODIFIED" ]; then
				MODIFIED="\"$mods\""
			else
				MODIFIED="$MODIFIED,\"$mods\""
			fi

		fi
	done <<< "$(echo "$COMMIT" | ./jq -r '.files[] | select (.status == "modified") | .filename')"
	while read rems; do
		if [ -n "$rems" ]; then
			if [ -z "$REMOVED" ]; then
				REMOVED="\"$rems\""
			else
				REMOVED="$REMOVED,\"$rems\""
			fi
		fi
	done <<< "$(echo "$COMMIT" | ./jq -r '.files[] | select (.status == "removed") | .filename')"

COMM_REFACTOR=$(cat <<EOT
{
  "commits": [
    {
      "id": "$fileline",
      "message": $MESSAGE,
      "timestamp": "$TIMESTAMP",
      "url": "https://github.com/$OWNER/$REPO/commit/$fileline",
      "author": {
        "name": "$AUTHOR_NAME",
        "email": "$AUTHOR_EMAIL"
      },
      "committer": {
        "name": "$AUTHOR_NAME",
        "email": "$AUTHOR_EMAIL"
      },
      "added": [
      $ADDED
      ],
      "removed": [
      $REMOVED
      ],
      "modified": [
      $MODIFIED
      ]
    }
  ],
  "head_commit": {
      "id": "$fileline",
      "message": $MESSAGE,
      "timestamp": "$TIMESTAMP",
      "url": "https://github.com/$OWNER/$REPO/commit/$fileline",
      "author": {
        "name": "$AUTHOR_NAME",
        "email": "$AUTHOR_EMAIL"
      },
      "committer": {
        "name": "$AUTHOR_NAME",
        "email": "$AUTHOR_EMAIL"
      },
      "added": [
      $ADDED
      ],
      "removed": [
      $REMOVED
      ],
      "modified": [
      $MODIFIED
      ]
    },
"repository": {
    "name": "$REPO",
    "full_name": "$OWNER/$REPO",
    "html_url": "https://github.com/$OWNER/$REPO",
    "description": ""
  }
}
EOT
)
	RAW_DIR="./$OWNER/$REPO/raw_events/push"
	mkdir -p "$RAW_DIR"
	echo "$COMM_REFACTOR" > "$RAW_DIR/$fileline.json"

	./retro_controller.cgi "$OWNER" "$REPO" "$fileline" "$COMM_REFACTOR"

#	if [ "$fileline" = "1a0a1a0600f70452513f14368beac81b5e3c0c6e" ]; then
#		exit 0;
#	fi
done <<< "$(echo "$COMMITS" | ./jq -r '.[] | .sha')"

exit 0
