#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <repos dir> <datasets dir> <diff number of tokens>"
	exit 1
fi

if [[ -z $3 ]]; then
	TOKENS=100
else
	TOKENS=$3
fi

echo "Using $TOKENS tokens"

mkdir -p $2

ls $1 |parallel -j 80 ./git2bitext.py -D $TOKENS -A -E $1/{} $2/{}
