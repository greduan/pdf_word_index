# PDF Word Index Creator

Simple project written as a Proof of Concept for the following requirements:

- Accepts a PDF, large or small
- Generates a word index for the given PDF (like the one you find at the back
  of books)
- Generates a new PDF with that index, nicely formatted
- Returns the ouptut for the user to be able to download right away

For example, for the given input in [docs/how_to_choose_your_people.pdf][input],
it generates the output [docs/output.pdf][output].

[input]: docs/how_to_choose_your_people.pdf
[output]: docs/output.pdf

## Setup

Requirements: `pyenv` installed, and Python version in `.python-version`
installed with pyenv.

```shell
make setup
make install
```

## Running

```shell
. venv/bin/activate
HOST='127.0.0.1' PORT='8080' PDF_WORD_INDEX_PASSWORD='asdf' python app.py
```

## Env vars

- HOST
- PORT
- PDF_WORD_INDEX_PASSWORD
