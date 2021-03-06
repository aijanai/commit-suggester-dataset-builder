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

min_tokens_msg_default=2
max_tokens_msg_default=30
max_tokens_diff_default=100

branches_search_chain = ['main', 'master', 'develop', 'devel']
branches_search_chain_string = ', '.join([f"'{x}'" for x in branches_search_chain])

stop_prefixes = ["rollback", "bump", "revert", "prepare version", "update changelog", "update gitignore", "update readme", "update submodule", "modify dockerfile", "modify makefile"]
stop_prefixes_string = ', '.join([f"'{x}'" for x in stop_prefixes])


parser = argparse.ArgumentParser(description="Generates a bitext from a git repository's log history, one with diff patches and the other with corresponding commit messages")
parser.add_argument("repo_path", help="Path to the repo location on the filesystem")
parser.add_argument("prefix", help="Input file prefix to search for <prefix>.diff and <prefix>.msg files")
parser.add_argument("-b", "--branch", default="auto", help=f"Git branch to scan (default: autodetect; fall back chain: {branches_search_chain_string}, then gives up and throws error)")
parser.add_argument("-P", "--no-pos-tagging", action="store_true", help="Skip POS tagging")
parser.add_argument("-E", "--skip-already-existing", action="store_true", help="Skip if already existing, without overwriting")
parser.add_argument("-T", "--include-trivial-commits", action="store_true", help=f"Don't skip commits beginning with following prefixes: {stop_prefixes_string}")
parser.add_argument("-A", "--only-atomic-commits", action="store_true", help="Skip commits with more than 1 file")
parser.add_argument("-C", "--cut-exceeding-diff", action="store_true", help="Do not throw away patches exceeding maximum length, but just cut them to the allowed maximum")
parser.add_argument("-m", "--min-tokens", default=min_tokens_msg_default, help=f"Minimum number of tokens per commit message (less will be skipped); default: {min_tokens_msg_default}")
parser.add_argument("-M", "--max-tokens-msg", default=max_tokens_msg_default, help=f"Maximum number of tokens in commit message (more will be skipped); default: {max_tokens_msg_default}")
parser.add_argument("-D", "--max-tokens-diff", default=max_tokens_diff_default, help=f"Maximum number of tokens in diff patch (more will be skipped); default: {max_tokens_diff_default}")
parser.add_argument("-v", "--verbose", action="store_true", help="More output")

args = parser.parse_args()

repo_path = args.repo_path
filename_prefix = args.prefix
verbose = args.verbose
min_tokens = int(args.min_tokens)
max_tokens_msg = int(args.max_tokens_msg)
max_tokens_diff = int(args.max_tokens_diff)
skip_pos_tagging = args.no_pos_tagging
cut_exceeding_diff = args.cut_exceeding_diff
include_trivial_commits = args.include_trivial_commits
skip_non_atomic_commits = args.only_atomic_commits
skip_already_existing = args.skip_already_existing
branch = args.branch

print(f"Parsing {repo_path}, ", end='', flush=True)

if skip_pos_tagging :
    print("will skip POS tagging, ", end='', flush=True)
if skip_already_existing :
    print("will skip existing files, ", end='', flush=True)
if skip_non_atomic_commits :
    print("will skip non atomic commits, ", end='', flush=True)

print(f"will skip messages lesser than {min_tokens} and longer than {max_tokens_msg} tokens", end='', flush=True)
if cut_exceeding_diff :
    print(f", cut patches longer than {max_tokens_diff}, ", end='', flush=True)
else:
    print(f", skip patches longer than {max_tokens_diff}, ", end='', flush=True)

if branch == "auto":

    print(f"detecting branch... ", end='', flush=True)

    found_default_branch = False

    for default_branch in branches_search_chain :

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
regex_nonascii = re.compile(r'[^\x00-\x7F]+')

tokenizer = WordPunctTokenizer()
if not skip_pos_tagging:
    nlp = spacy.load("en_core_web_sm")


repo = RepositoryMining(repo_path, only_in_branch=branch, only_no_merge=True)

if os.path.isfile(output_diff):
    if skip_already_existing :
        sys.exit(0)
    else:
        os.unlink(output_diff)

if os.path.isfile(output_msg):
    if skip_already_existing :
        sys.exit(0)
    else:
        os.unlink(output_msg)

total = 0
added = 0

def _get_condition_starts_with_a_verb(doc, prepended=False):

    if prepended :
        if len(doc) > min_tokens:
            return (doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT' or doc[2].pos_ == 'VERB' or doc[2].dep_ == 'ROOT')
        else:
            return (doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT')
    else:
        return (doc[0].pos_ == 'VERB' or doc[0].dep_ == 'ROOT' or doc[1].pos_ == 'VERB' or doc[1].dep_ == 'ROOT')


def _clean_msg_string(msg):
    # limit message to 1K since we are taking only first sentence
    msg = msg[:1000]
    msg = msg.split("\n")[0]
    msg = msg.replace("\r",'')
    msg = re.sub(regex_issue, '#ISSUE', msg)
    msg = re.sub(regex_nonascii, '', msg)

    msg = msg.lower()
    return msg


def _clean_diff_string(diff):
    # limit patch to 100KB
    diff = diff[:100000]
    diff = diff.strip(" \r\n")
    diff = diff.replace("\n", " <nl> ")
    diff = re.sub(regex_offset, '', diff)
    diff = re.sub(regex_nonascii, '', diff)
    return diff


def _is_valid_msg(msg):
    doc = nlp(msg)

    # at least 2 words commit message
    if len(doc) < min_tokens or len(doc) > max_tokens_msg:
        print("l", end='')
        return False

    if not include_trivial_commits:
       for stop_word in stop_prefixes:
            stop_word = stop_word.split(" ")
            # skip trivial messages as per "Liu et al., 2018"
            if len(stop_word) > 1:
                condition = stop_word[0] in doc[0].text.lower() and stop_word[1] in doc[1].text.lower()
            else:
                condition = stop_word[0] in doc[0].text.lower()

            if condition :
                print("t", end='')
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
               print(f"skipping {msg} ", end='')
            else:
                print("s", end='')
            return False

    return True


def _is_valid_diff(diff_line_str):
    doc = nlp(diff_line_str)

    if len(doc) > max_tokens_diff :
        return False
    else:
        return True


def _get_diff_string(modifications):
    diff_line = []

    if skip_non_atomic_commits and len(modifications)>1 :
        print("a", end='')
        return ''

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
           diff_line.append(diff)

    if len(diff_line) == 0:
        print("-", end='')
        return ''

    diff_line_str = _recompile_tokenized_diff(diff_line)

    if not _is_valid_diff(diff_line_str):
        if not cut_exceeding_diff :
            print("l", end='')
            return ''
        else:
            doc = nlp(diff_line_str)
            doc = doc[:max_tokens_diff]
            diff_line = [ x for x.text in doc]
            diff_line_str = _recompile_tokenized_diff(diff_line)
            print("c", end="")

    return diff_line_str

def _recompile_tokenized_diff(diff_line):
    diff_line_str = ' '.join(diff_line).strip()
    diff_line_str = ' '.join([token.strip() for token in tokenizer.tokenize(diff_line_str)]).replace("< nl >", "<nl>")
    return diff_line_str


def process(commit):
    msg = _clean_msg_string(commit.msg)

    if not skip_pos_tagging:
        if not _is_valid_msg(msg):
            msg = ''

    if len(msg) > 0:
        diff = _get_diff_string(commit.modifications)
    else:
        # no need to parse diff patch, if msg is empty
        diff = ''

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
