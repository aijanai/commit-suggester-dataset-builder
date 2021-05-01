#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <datasets dir>"
	exit 1
fi

#ls $1| sed 's/\.msg$//g' | sed 's/\.diff$//g' | sort -u |parallel -j 30 ./split_test_train_valid.py -v $1/{}


cat $1/*.valid.msg > dataset.valid.msg
cat $1/*.valid.diff > dataset.valid.diff
cat $1/*.test.diff > dataset.test.diff
cat $1/*.test.msg > dataset.test.msg
cat $1/*.train.msg > dataset.train.msg
cat $1/*.train.diff > dataset.train.diff
