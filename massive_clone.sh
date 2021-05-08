#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <repos file>"
	exit 1
fi

TMP_FILE=/tmp/massive_clone

echo /dev/null > $TMP_FILE

cat $1 |while read i; do echo "git clone --bare $i $(echo $i|awk 'BEGIN{FS="/"}{printf("%s-%s\n",$4,$5)}')" >> $TMP_FILE ; done

parallel -j 30 < $TMP_FILE

rm $TMP_FILE
