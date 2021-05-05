#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <repos dir> <datasets dir>"
	exit 1
fi

mkdir -p $2

ls $1 |parallel -j 80 ./build_dataset.py -A -E $1/{} $2/{}
