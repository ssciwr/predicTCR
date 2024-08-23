# predicTCR Backend

The Flask REST API backend for predicTCR.

Note: these are development install/use instructions, see
[README_DEV.md](https://github.com/ssciwr/predicTCR/blob/main/README_DEV.md)
for instructions on running the full production docker compose setup locally.

## Installation

```pycon
pip install -e .[tests]
```

## Use

To start a local development server for testing purposes:

```bash
predicTCR_server
```

Type `predicTCR_server --help` to see the command line options:

```bash
Usage: predicTCR_server [OPTIONS]

Options:
  --host TEXT       [default: localhost]
  --port INTEGER    [default: 8080]
  --data-path TEXT  [default: .]
  --help            Show this message and exit.
```

## Tests

```pycon
pytest
```
