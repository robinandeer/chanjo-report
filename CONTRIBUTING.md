# Contributing
All contributions are much welcome and greatly appreciated! Expect to be credited for you effort.

This document is adapted from the cookiecutter [CONTRIBUTING.rst][cookie-contrib].


## General
Generally try to limit the scope of any Pull Request to an atomic update if possible. This way, it's much easier to assess and review your changes.

You should expect a considerably faster turn around if you submit two or more PRs instead of baking them all into one major PR.


## Issue tracker
chanjo-report uses the excellent [GitHub issue tracker][issues].


## Types of Contributions
There are many ways you can help out and improve this repository.

### Report Bugs
Report bugs at [robinandeer/chanjo-report/issues][issues].

Consider including the following data in your bug report:

- Your operating system name and version
- Any details about your local setup that might be helpful in troubleshooting
- If you can, provide detailed steps to reproduce the bug
- If you don't have steps to reproduce the bug, just note your observations in as much detail as you can. Questions to start a discussion about the issue are welcome.

### Fix Bugs
Look through the [GitHub issues][issues] for bugs. Anything tagged with "bug" is open to whoever wants to implement it. A good idea is also to review the comment thread to see if the issue is already referenced in any open pull requests.

### Implement Features
Look through the [GitHub issues][issues] for features. Anything tagged with "feature" is open to whoever wants to implement it.

### Write Documentation
Chanjo Report could always use more documentation, whether as part of the official Chanjo Report docs, in inline docstrings, or even on the web in blog posts, articles, and such.

If you have written your own tutorial or review of the software, please consider adding a refferal link to the repository.

### Submit Feedback
The best way to send feedback is to [open a new issue][issues].

If you are requesting a feature:

- Explain in detail how it would work
- Keep the scope as narrow as possible, to make it easier to implement (atomic)


## Get Started!
Ready to contribute? Here's how to set up `Chanjo Report` for local development.

> Over time my ambition is to provide a reproducable and automated setup through Vagrant.

1. Fork the [robinandeer/chanjo-report][repo] repo on GitHub

2. Clone your fork locally:

  ```bash
  $ git clone git@github.com:<your github username>/chanjo-report.git
  ```

  I would personally recommend [SourceTree][sourcetree] as an excellent GUI for git.

3. Install [uv][uv] if you don't have it, then sync the project into a virtual environment. `uv` reads `pyproject.toml` and the committed `uv.lock`, so everyone gets the same dependency versions:

  ```bash
  $ cd chanjo-report/
  $ uv sync
  ```

  Run commands inside that environment with `uv run`, for example `uv run pytest`.

4. Create a branch for local development:

  ```bash
  $ git checkout -b name-of-your-bugfix-or-feature
  ```

5. Make you changes locally

6. When you're done making changes, check that your changes pass the linter, the formatter and the tests:

  ```bash
  $ uv run ruff check .
  $ uv run ruff format --check .
  $ make test
  ```

  `make test` runs the test suite in Docker containers, against a MariaDB database, the same as CI. It needs only Docker. To run a subset, pass `TESTS=tests/test_server.py`. Use `uv run pytest tests` for a faster run against a temporary SQLite database on your machine.

7. Commit your changes and push your branch to GitHub:

  ```bash
  $ git add .
  $ git commit -m "Detailed description of your changes."
  $ git push origin name-of-your-bugfix-or-feature
  ```

8. Check that the test coverage hasn't dropped:

  ```bash
  $ uv run coverage run -m pytest tests
  $ uv run coverage report -m
  ```

9. Submit a pull request through the GitHub website. I would encourage you to submit your pull request early in the process. This makes it easier to maintain an overview of current development and opens up for continous discussion.


## Pull Request Guidelines
Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.

3. The pull request should pass the GitHub Actions workflow in `.github/workflows/tests.yml`, which runs the linter and tests on Python 3.14.


## Coding conventions
Generally I recommend two ways to stay up-to-date on chanjo-report coding standards.

1. Read and pay attention to current code in the repository

2. Install a plugin for [EditorConfig][editorconfig] and let it handle some of the detailed settings for you.


## Tips
To run a particular test:

```bash
$ uv run pytest tests/test_server.py::test_gene
```

To run a subset of tests:

```bash
$ uv run pytest tests -k report
```


[uv]: https://docs.astral.sh/uv/
[cookie-contrib]: https://github.com/audreyr/cookiecutter/blob/master/CONTRIBUTING.rst
[editorconfig]: http://editorconfig.org/
[issues]: https://github.com/robinandeer/chanjo-report/issues
[repo]: https://github.com/robinandeer/chanjo-report
[sourcetree]: http://www.sourcetreeapp.com/
