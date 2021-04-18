# commit-suggester-dataset-builder
Utilities to massively download GitHub repositories and parse theis history log into a dataset


## Getting started
### Downloading repo data
```
export CREDENTIALS=<github-user>:<github-api-key>
export LANGUAGE=java
./make_top_github_repos.sh
```

### spacy initialization
Download POS tagger data for English (small version):
```
python -m spacy download en_core_web_sm
```

### Running the parser
A repository and a file name prefix are expected.
For example:
```
./build_dataset.py ~/librosa.git current -b main
```
parses the local repository `librosa.git`, scanning branch `main` and writing the 2 files `current.msg` and `current.diff`, respectively containing commit messages and related diff.

Help is available with:
```
./build_dataset.py -h
```
