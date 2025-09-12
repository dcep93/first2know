from pathlib import Path

with open(Path(__file__).parent / "fetch_wrapped.js") as fh:
    contents = fh.read()


def fetch_wrapped():
    pass
