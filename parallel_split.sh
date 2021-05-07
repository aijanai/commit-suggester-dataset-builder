#!/bin/bash

if [[ $# -lt 2 ]]; then
	echo "Usage: $0 <datasets dir> <prefix>"
	exit 1
fi

ls $1| sed 's/\.msg$//g' | sed 's/\.diff$//g' | sort -u |parallel -j 30 ./split_test_train_valid.py -v $1/{}


cat $1/*.valid.msg | tr A-Z a-z > $2.valid.msg
cat $1/*.valid.diff | tr A-Z a-z > $2.valid.diff
cat $1/*.test.diff | tr A-Z a-z > $2.test.diff
cat $1/*.test.msg | tr A-Z a-z > $2.test.msg
cat $1/*.train.msg | tr A-Z a-z > $2.train.msg
cat $1/*.train.diff | tr A-Z a-z > $2.train.diff
