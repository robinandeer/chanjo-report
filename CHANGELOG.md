# Change log

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
