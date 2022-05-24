**duden-scraper** is a tool to scrape information from lemmas in duden.de


The tool is currently in pre-alpha status. The interface is probably going to be
extended, including backwards-compatibilty breaking changes.  When using the
tool, take into account that it is highly probable that the project will be
abandoned at all.


# Liability Notice

duden.de might forbid scraping. The author of the tool does not assume any
reponsibility for legal concerns that might raise from you using the tool.
It is your liability as a user of the tool to check whether scraping duden.de
violates the site's policies and to make sure that you comply with the site's
policy. It is also your liability to check whether using the tool is legal.


# Prerequisites

The tool requires Python3.10 and some dependencies which can be installed with
pip:

```
$ pip install -r requirements-prod.txt
```

You might want to consider using a [virtual
environment](https://docs.python.org/3/tutorial/venv.html) when installing the
dependencies.


# Run

Run the scraper by calling `python duden-scraper/cli.py`. The script takes the following
parameters:

+ `--output_path` / `-o` (required): The path to store the results csv file. The
  file must not exist yet.
+ `--search` (required): The search term to start the lemma search with.
+ `--part-of-speech` / `-pos` (optional): Restrict the results to lemmas whose
  part of speech ("Wortart") is amongst the provided ones. Accepted values are:
  `Verb`, `Adjektiv`, `Substantiv`.
+ `--starts-with` (optional): Restrict results to lemmas which start with the
  provided string.
+ `--does-not-start-with` (optional): Restrict results to lemmas which do not
  start with any of the provided strings.
+ `--extract` (optional): Which features to extract from the lemma. Defaults to
  `url, title, part-of-speech`, `hyphenation`.
