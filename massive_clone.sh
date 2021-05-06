#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <repos file>"
	exit 1
fi

cat $1 |while read i; do git clone --bare $i $(echo $i|awk 'BEGIN{FS="/"}{printf("%s-%s\n",$4,$5)}'); done
