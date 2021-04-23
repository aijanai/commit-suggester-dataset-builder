#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <repos dir> <datasets dir>"
	exit 1
fi

ls $1 |parallel -j 30 ./build_dataset.py -E $1/{} $2/{}
