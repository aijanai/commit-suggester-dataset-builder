# git2bitext: a tool to derive a "git patches" to "commit messages" bitext from a git repo as "source" to "target" language mapping
Utility to massively download GitHub repositories and parse theis history log into a dataset for machine translation.


## Getting started
### Downloading repo data
```
export CREDENTIALS=<github-user>:<github-api-key>
export LANGUAGE=java
./make_top_github_repos.sh
```

### spacy initialization
Download Spacy POS tagger data for English (small version):
```
python -m spacy download en_core_web_sm
```

### Running the parser
A repository and a file name prefix are expected.
For example:
```
./git2bitext.py ~/librosa.git current -b main
```
parses the local repository `librosa.git`, scanning branch `main` and writing the 2 files `current.msg` and `current.diff`, respectively containing commit messages and related diff. Omitting `-b` flag triggers an autodetection of main branch.

Help is available with:
```
./git2bitext.py -h
```
