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

### Splitting the files
The utility `./split_test_train_valid.py` can assist in generating the splits (80% train, 10% validation, 10% test) from the bitexts.

### Crawling the data from online repo
`massive_clone.sh` reads a text file with one repo per line and parallely downloads the repos.  
`make_top_github_repos.sh` builds the text file with the top 1000 repositories for a given programming language. Needs GitHub credentials set as $CREDENTIALS env var and a language name set at $LANGUAGE env var.  
`parallel_generation.sh` launches git2bitext.py in parallel.
`parallel_split.sh` splits the bitexts in parallel.
