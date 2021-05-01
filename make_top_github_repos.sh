#!/bin/bash

LANGUAGE=${LANGUAGE:-python}
REPO_LIST=top-$LANGUAGE-github.txt

cat /dev/null > $REPO_LIST

echo "LANGUAGE=$LANGUAGE"

for i in $(seq 1 300); do
  echo $i
  curl -s  -H "Accept: application/vnd.github.v3+json" -u $CREDENTIALS\
    "https://api.github.com/search/repositories?q=language:$LANGUAGE&sort=stars&order=desc&page=$i" |jq -r '.items[].clone_url' >> $REPO_LIST
  if [[ $? -ne 0 ]]; then
    exit 0
  fi
  sleep 3
done
