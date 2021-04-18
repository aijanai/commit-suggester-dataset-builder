#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydriller import RepositoryMining
import re
import os

regex_offset = re.compile("@@.+?@@") 
regex_issue = re.compile("#[0-9]+")

repo = RepositoryMining("~/librosa.git", only_in_branch='main', only_no_merge=True)

for commit in repo.traverse_commits():

    msg = commit.msg
    msg = msg.split("\n")[0]
    msg = re.sub(regex_issue, '#ISSUE', msg)

    print(f"{msg}")

    for i, modified_file in enumerate(commit.modifications): # here you have the list of modified files
        diff = modified_file.diff
        diff = diff.replace("\n", " <nl> ")
        diff = re.sub(regex_offset, '', diff)

        if modified_file.old_path is None:
           print(f"added {modified_file.new_path} <nl> ",end=' ')
           continue

        if modified_file.new_path is None:
           print(f"deleted {modified_file.new_path} <nl> ",end=' ')
           continue

        if modified_file.new_path is not None and modified_file.old_path is not None:
           print(f"modified {modified_file.new_path} <nl> ",end=' ')
           print(diff, end=' ')

    print()
