# Change log

## [unreleased]
### Added
- Tests that load demo data into a SQLite chanjo database and request the report, gene, JSON and PDF routes, run in CI on every pull request
### Changed
- Python moved from 3.12 to 3.14, in `.python-version`, the Dockerfiles and the test image
- Packaging moved from `setup.py`, `setup.cfg`, `MANIFEST.in` and `requirements*.txt` to a single `pyproject.toml` (hatchling); dependencies are locked in `uv.lock`, installed with `uv sync` and built with `uv build`
- Lint and formatting use ruff; CI runs `ruff check` and `ruff format --check`
- The Babel `.mo` translation catalogue is compiled during the build and included in the wheel
- Dockerfile installs dependencies from `uv.lock`
- Tests run in Docker containers with `make test`, against MariaDB 11 as in production. CI runs the same target
- Removed the obsolete Travis config and `invoke` tasks

### Removed
- Unused `pyscss` dependency. SCSS compilation was removed in 2014 and the package ships plain CSS, but the requirement was never dropped. It is a source-only package that cannot be installed without a build step.
- Other unused dependencies: `Flask-DebugToolbar`, `lxml`, `path.py`, `six`, `tabulate`, `toml`, `toolz` and `importlib_resources`

### Fixed
- `pretty_date` showed "0 years ago" for any date less than a year old
- Typo `msgif` for `msgid` in the Swedish catalogue (no template uses that string yet)
- `docs/conf.py` had a syntax error that broke the Sphinx build

## 4.12.3 (2026-10-02)
### Fixed
- Build with latest chanjo 4.9.2 including the sqlalchemy async io fix

## 4.12.2 (2026-05-08)
### Fixed
- Order of data returned in the `samplesex_rows` function (#89)

## 4.12.1 (2026-05-08)
### Fixed 
- Update automation, bump chanjo version to 4.9.1

## 4.12.0 (2025-10-29) 
### Added
- Enable PEP 660–compatible editable installs (`pip install -e`) (#81)
### Changed
- Replaced Flask-weasyprint (cairo and pango-based) with pdfkit (#79)
- Removed `https://bootswatch.com/simplex/bootstrap.min.css` lib import from two base layouts since it's no longer available (#83)
### Fixed
- Healthcheck in Docker demo setup (#77)
- `chanjo report --render pdf` command now accepting a list of samples and output file (#80)

## 4.11.5 (2025-08-13)
### Fixed
- Update automation with slightly older python, and explicit setuptools

## 4.11.5 (2025-08-13)
### Fixed
- Update automation with slightly older python (3.10), and explicit setuptools
- Bump version and fix changelog
- Once more, test with 3.12 and explicit setuptools install in automation

## 4.11.4 (2025-08-13)
### Fixed
- Update automation with newer images to allow e.g. pypi deployment

## 4.11.3 (2025-03-13)
### Fixed
- Removed `webassets` via removal of unused Flask-Assets dependency

## 4.11.2 (2024-11-10)
### Changed
- Updated Dockerfile to use Python 3.12
### Fixed
- Deprecate pkg_resources
- Healthcheck of MariaDB container in docker-compose.yml

## 4.11.1 (2024-06-05)
### Fixed
- Added cryptography module among the dependencies

## 4.11 (2024-05-23)
### Changed
- Removed alchy dependency
### Fixed
- Timeout when creating genes overview due to slow transcript_stat query

## 4.10.2 (2023-08-16)
### Fixed
- Timeout when creating report due to slow transcript_stat query

## 4.10.1 (2023-03-10)
### Fixed
- Fix GitHub Actions PyPi automation 

## 4.10 (2023-03-07)
### Added
- Documentation for Docker demo build
### Fixed
- Update from deprecated Ubuntu base image for the PyPi build publish flow

## 4.9.4 (2023-03-06)
### Changed
- Remove one more use of GET and flask session storage to avoid overloading the session cookie
### Fixed
- Use virtual environment and multi-stage build in Dockerfile
- `Babel` object has no attribute `localeselector` error at startup

## 4.9.3 (2022-04-26)
### Changed
- Install requirements from requirements file parsed in setup.py
### Fixed
- Error launching the app due to `LocalStack.__ident_func__` missing in werkzeug >= 2.1.x

## 4.9.2 (2022-02-07)
### Fixed
- App crashing when unsupported gene IDs are provided in the report endpoint

## 4.9.1 (2022-01-20)
### Fixed
- Typo in Makefile preventing loading of demodata
- Multisample PDF reports

## 4.9 (2022-01-19)
- GitHub action to push repo to PyPI on new release event

## 4.8 (2020-11-20)
### Added
- docker-compose and Makefile
### Changed
- Removed ENTRYPOINT from Dockerfile

## 4.7 (2020-11-16)
### Added
- Dockerfile

## 4.6 (2020-09-30)
### Added
- Endpoint that returns mean coverage over all transcripts of a cromsosome for a list of samples, in json
### Fixed
- Value returned by the endpoint collecting mean coverage over genes, returning json objects

## 4.5 (2020-09-29)
### Added
- Endpoint that returns mean coverage over one or more genes for a list of samples, in json

## 4.4.1 (2020-04-27)
### Fixed
- return error message when users provide a non-numerical list of gene IDs

## 4.4.0 (2020-04-23)
### Added
- POST gene_ids in genes list navigation

## 4.3.0 (2020-04-23)
### Added
- pdf method with download option saves report with case display name now


## 3.2.0 (2019-02-25)
### Added
POST gene_ids in genes view

## 3.0.2 (2016-03-08)
### Added
- option to pass link to gene view

## 3.0.1 (2016-03-08)
### Fixed
- minor issues in genes view

## 3.0.0 (2016-03-08)
### Adds
- Support for new transcript schema in chanjo v3.4.0

### Removed
- Support for default exon focused schema in previous version of chanjo

## 2.6.1 (2016-03-01)
### Fixed
- generate links with joined gene ids

## 2.6.0 (2016-02-29)
### Added
- Add overview of transcripts (for list of genes)

### Changed
- Show 404 if gene not found for gene overview

## 2.5.1 (2016-02-25)
### Changed
- Order completeness levels in plot and update colors
- Use CDNJS for highcharts to support also HTTPS

## 2.5.0 (2016-02-25)
### Added
- A new gene overview for all or a subset of samples
- Include chanjo repo in Vagrant environment

## 2.4.1 (2016-02-23)
### Fixed
- correctly fetch database uri using CLI

## 2.4.1 (2016-01-29)
### Fixed
- roll back after `OperationalError`

## 2.4.0 (2016-01-13)
### Added
- handle post/get requests for the coverage report (URL limits)
- new "index" blueprint which displays list of samples and genes

### Removed
- link to the "index" page from the report (security)

### Changed
- use a customized version of the HTML form for the PDF link in the navbar
- avoid searching for group id if sample ids are submitted in query
- use "select" element for picking completeness level

### Fixed
- removes the "submit" label from the customizations form
- look up "show_genes" from correct "args/form" dict

## 2.3.2 (2016-01-04)
### Fixed
- handle white-space in gene ids

## 2.3.1 (2015-12-22)
### Changed
- updates how to call diagnostic yield method to explicitly send in exon ids

## 2.3.0 (2015-11-18)
### Adds
- add ability to change sample/group id in report through query args

## 2.2.1 (2015-11-18)
### Changes
- improved phrasing of explanations and other translations

## 2.2.0 (2015-11-16)
### Added
- ability to determine lang by setting query arg in URL
- add uploaded date to report per sample

### Changed
- rename "gender" as "sex"
- clarify explanations, rename "diagnostic yield"

### Fixed
- update to Python 3.5 and fix travis test setup
- stay on "groups" route for PDF report

## 2.1.0 (2015-11-04)
### Added
- Customization options for report
- Link to PDF version of report

### Changed
- Updated chanjo requirement

## 2.0.1 (2015-11-03)
### Fixed
- Include missing template files in dist
- Include more translations

## 2.0.0 (2015-11-03)
### Changed
- Adds support for Chanjo 3
- Layout of report is more condensed
- Updated APIs across the board

## 1.0.1 (2015-06-01)
### Fixed
- Fix bug in diagnostic yield method

## 1.0.0 (2015-06-01)
### Fixed
- Fix issue in diagnostic yield for small gene panels

## 1.0.0-rc1 (2015-04-15)
### Fixed
- Changes label for gender prediction

## 0.0.13 (2015-04-13)
### Fixed
- Breaking bug in CLI when not setting gene panel

## 0.0.12 (2015-04-13)
### Added
- Add explanation of gender prediction in report

### Changed
- Handle extensions of intervals (splice sites) transparently in report
- Update text in report (eng + swe)

### Fixed
- Avoid error when not setting a gene panel + name in CLI

## 0.0.11 (2015-04-08)
### Changed
- Enable setting name of gene panel (PANEL_NAME) from command line

## 0.0.10 (2015-03-22)
### Fixed
- Remove duplicate call to ``configure_extensions``

## 0.0.9 (2015-03-21)
### Changed
- Keep scoped session chanjo api inside ``current_app`` object

## 0.0.8 (2015-03-21)
### Changed
- Change default log folder to ``/tmp/logs``
- Rename info log to more specific ``chanjo-report.info.log``

## 0.0.7 (2015-03-03)
### Changed
- Add a splash of color to HTML/PDF report (CSS only)
- Change name from ``HISTORY.md`` to ``CHANGELOG.md``

## 0.0.6 (2015-02-25)
### Fixed
- Incorrect template pointers in "package_data"

## 0.0.5 (2015-02-25)
### Fixed
- Namespace templates for "report" Blueprint under "report"
