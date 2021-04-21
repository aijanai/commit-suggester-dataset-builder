#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydriller import RepositoryMining
import git
import sys
import re
import os
import argparse
import spacy
from nltk.tokenize import WordPunctTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("repo_path", help="Path to the repo location on the filesystem")
parser.add_argument("prefix", help="Input file prefix to search for <prefix>.diff and <prefix>.msg files")
parser.add_argument("-b", "--branch", default="auto", help="Git branch to scan (default: autodetect; fall back chaim: 'master', 'main', 'develop', then throws error")
parser.add_argument("-nopos", "--no-pos-tagging", action="store_true", help="Skip POS tagging")
parser.add_argument("-v", "--verbose", action="store_true", help="Suppress output")

args = parser.parse_args()

repo_path = args.repo_path
filename_prefix = args.prefix
verbose = args.verbose
nopos = args.no_pos_tagging
branch = args.branch

print(f"Parsing {repo_path}, ", end='', flush=True)

if branch == "auto":

    print(f"detecting branch... ", end='', flush=True)

    found_default_branch = False

    for default_branch in ['master', 'main', 'develop', 'devel']:

        if found_default_branch:
            break

        try:
            repo = RepositoryMining(repo_path, only_in_branch=default_branch, only_no_merge=True)

            for commit in repo.traverse_commits():
                check = commit.msg

                if check is not None:
                    found_default_branch = True
                    branch = default_branch
                    print(f"using {branch}", flush=True)
                    break

        except git.exc.GitCommandError as gce:
            continue

    if not found_default_branch:
        print(f"Can't detect default branch", flush=True)
        sys.exit(1)
else:
    print(f"branch {branch}", flush=True)

output_diff = f"{filename_prefix}.diff"
output_msg = f"{filename_prefix}.msg"

regex_offset = re.compile("@@.+?@@")
regex_issue = re.compile("#[0-9]+")

tokenizer = WordPunctTokenizer()
if not nopos:
    nlp = spacy.load("en_core_web_sm")


repo = RepositoryMining(repo_path, only_in_branch=branch, only_no_merge=True)

if os.path.isfile(output_diff):
    os.unlink(output_diff)

if os.path.isfile(output_msg):
    os.unlink(output_msg)

total = 0
added = 0

def _get_condition_starts_with_a_verb(doc, prepended=False):

    if prepended :
        if len(doc) > 2:
            return (doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT' or doc[2].pos_ == 'VERB' or doc[2].dep_ == 'ROOT')
        else:
            return (doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT')
    else:
        if len(doc) > 1:
            return (doc[0].pos_ == 'VERB' or doc[0].dep_ == 'ROOT' or doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT')
        else:
            return (doc[0].pos_ == 'VERB' or doc[0].dep_ == 'ROOT')


def _clean_msg_string(msg):
    msg = msg.split("\n")[0]
    msg = re.sub(regex_issue, '#ISSUE', msg)

    msg = msg.lower()
    return msg


def _clean_diff_string(diff):
    diff = diff.strip(" \r\n")
    diff = diff.replace("\n", " <nl> ")
    diff = re.sub(regex_offset, '', diff)
    return diff


def _is_valid_msg(msg):
    doc = nlp(msg)

    if len(doc)==0:
        print("-", end='')
        return False

    if "rollback" in doc[0].text:
        print("r", end='')
        return False

    starts_with_a_tag = "[" == msg[:1]

    if starts_with_a_tag :

        tmp = msg.split()
        _ = tmp.pop(0)
        msg = ' '.join(tmp)

        return _is_valid_msg(msg)

    if not _get_condition_starts_with_a_verb(doc, prepended=False):

        # sometimes POS taggers misinterpret verbs for adjectives; add leading "I" as per "van Hal et al., 2019" V-DO relaxation workaround
        doc_prepended = nlp(f"I {msg}")

        if not _get_condition_starts_with_a_verb(doc, prepended=True):
            if verbose:
               print(f"skipping {msg}", end='')
            else:
                print("s", end='')
            return False

    return True


def _get_diff_string(modifications):
    diff_line = []

    for i, modified_file in enumerate(modifications): # here you have the list of modified files
        diff = _clean_diff_string(modified_file.diff)

        if modified_file.old_path is None:
           diff_line.append(f" added {modified_file.new_path}")
           continue

        if modified_file.new_path is None:
           diff_line.append(f" deleted {modified_file.old_path}")
           continue

        if modified_file.new_path is not None and modified_file.old_path is not None:
           diff_line.append(f" modified {modified_file.new_path}")
           diff_line.append("<nl>")
           diff_line.append(diff[:500])

    if len(diff_line) == 0:
        print("-", end='')
        return ''

    diff_line_str = ' '.join(diff_line).strip()
    diff_line_str = ' '.join([token.strip() for token in tokenizer.tokenize(diff_line_str)]).replace("< nl >", "<nl>")

    return diff_line_str


def process(commit):
    msg = _clean_msg_string(commit.msg)

    if not nopos:
        if not _is_valid_msg(msg):
            msg = ''

    diff = _get_diff_string(commit.modifications)

    return (msg, diff)


with open(output_diff,"a+") as fp_diff_out:
    with open(output_msg,"a+") as fp_msg_out:

        for commit in repo.traverse_commits():
            total += 1

            msg, diff_line_str = process(commit)

            if len(msg) > 0 and len(diff_line_str) > 0:
                added += 1

                fp_msg_out.write(msg + "\n")
                fp_diff_out.write(diff_line_str + "\n")
                print(".", end='', flush=True)

print(flush=True)

print(f"Validated and saved {100*round(added/total,4)}% of commits on branch {branch}")
