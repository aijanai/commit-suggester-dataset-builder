# commit-suggester-dataset-builder
Utility to parse a git repo history log into a dataset


## Getting started
### spacy initialization
Download POS tagger data for English (small version):
```
python -m spacy download en_core_web_sm
```

### Running it
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
