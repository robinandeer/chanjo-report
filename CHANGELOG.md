# Change log

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
