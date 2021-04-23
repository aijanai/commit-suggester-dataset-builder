#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import csv

parser = argparse.ArgumentParser()
parser.add_argument("filename_prefix_path", help="Prefix path to the couple of files we want to split. It expects .msg and .diff files for the given prefix path.")
parser.add_argument("-v", "--verbose", action="store_true", help="Debug output")

args = parser.parse_args()

filename_prefix = args.filename_prefix_path
verbose = args.verbose

if verbose:
    print(f"Splitting {filename_prefix} ")

input_diff = f"{filename_prefix}.diff"
input_msg = f"{filename_prefix}.msg"

output_train_diff = f"{filename_prefix}.train.diff"
output_train_msg = f"{filename_prefix}.train.msg"

output_test_diff = f"{filename_prefix}.test.diff"
output_test_msg = f"{filename_prefix}.test.msg"

output_valid_diff = f"{filename_prefix}.valid.diff"
output_valid_msg = f"{filename_prefix}.valid.msg"

for i in [output_train_diff, output_train_msg, output_test_diff, output_test_msg, output_valid_msg, output_valid_diff] :
    if os.path.isfile(i):
        os.unlink(i)

with open(input_diff,"r+") as fp_diff_in:
    with open(input_msg,"r+") as fp_msg_in:
        with open(output_train_diff,"a+") as fp_diff_train:
            with open(output_train_msg,"a+") as fp_msg_train:
                with open(output_test_diff,"a+") as fp_diff_test:
                    with open(output_test_msg,"a+") as fp_msg_test:
                        with open(output_valid_diff,"a+") as fp_diff_valid:
                            with open(output_valid_msg,"a+") as fp_msg_valid:

                                diffs = [i.strip() for i in list(fp_diff_in)]
                                msgs = [i.strip() for i in list(fp_msg_in)]
                        
                                df_msg = pd.DataFrame(msgs, columns =['msg'])
                                df_diff = pd.DataFrame(diffs, columns =['diff'])
                        
                        
                                X_train, X_test, y_train, y_test = train_test_split(df_diff, df_msg, test_size=0.20, random_state=42)
                        
                                X_test, X_valid, y_test, y_valid = train_test_split(X_test, y_test, test_size=0.50, random_state=42)
                        
                                for i in list(y_train['msg']):
                                    fp_msg_train.write(i+"\n")

                                for i in list(X_train['diff']):
                                    fp_diff_train.write(i+"\n")

                                for i in list(y_test['msg']):
                                    fp_msg_test.write(i+"\n")

                                for i in list(X_test['diff']):
                                    fp_diff_test.write(i+"\n")

                                for i in list(y_valid['msg']):
                                    fp_msg_valid.write(i+"\n")

                                for i in list(X_valid['diff']):
                                    fp_diff_valid.write(i+"\n")

