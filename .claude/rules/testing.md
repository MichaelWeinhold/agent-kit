---
paths:
  - "tests/**"
---

# Writing tests here

- **Never let a test reach GitHub.** Replace `gh` with a fake that returns recorded JSON;
  a test that needs git builds a repository under `tmp_path`.
- **Each test gets fresh state** — `tmp_path`, never a file under the repository.
- **Drive a script through its `main(argv)` or a pure function**, and assert on the exit
  code and on what it printed to stdout and stderr.

## Conventions this repository already follows

- `S101`, `S105` and `S106` are off under `tests/`. Give anything else a test needs
  suppressed its own `per-file-ignores` entry in `pyproject.toml`, never a blanket
  widening of `tests/*`.
- Annotate tests too: `ANN` is on for the whole tree.
- A test that shells out names its binary and gets `S603`/`S607` suppressed for that file
  alone.

## Running the suite

Replay a red with the `--randomly-seed=<n>` it printed, never a retry. Debug one test with
`-p no:randomly`; never pin an order.
