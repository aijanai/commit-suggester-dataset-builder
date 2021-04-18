#!/bin/bash
REPO_LIST=top-python-github.json
cat /dev/null > $REPO_LIST


for i in $(seq 1 300); do
  echo $i
  curl -s  -H "Accept: application/vnd.github.v3+json" -u $CREDENTIALS\
    "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&page=$i" |jq -r '.items[].clone_url' >> $REPO_LIST
  sleep 3
done
