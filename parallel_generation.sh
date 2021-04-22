#!/bin/bash

cat repos|parallel -j  ./build_dataset.py -E ../top_github_python/{} datasets/{}
