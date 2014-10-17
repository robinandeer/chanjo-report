# Chanjo Report [![PyPI version][fury-image]][fury-url] [![Build Status][travis-image]][travis-url]

## Purpose
Chanjo Report automatically generates basic coverage reports from Chanjo SQL databaes. It works as a plugin to Chanjo by adding a subcommand to its CLI.

The idea for the inital release is to define a small set of interesting coverage metrics.


## Features
- Input formats
  - Chanjo SQL database

- Render formats
  - text: easily parable and pipeable
  - PDF: easily distributable (for humans)
  - json: easily transferrable (over networks)
  - HTML: easily deliverable

- Translations/languages
  - English
  - (Swedish)

- One process/one command


## Motivation
The HTML report comes as mostly a side effect of the PDF rendering. The plugin has a built in Flask server that can render dynamic reports on request and displays in a browser on [localhost](http://localhost:5000/).


## Implementation
Chanjo Report will be built as separate modules that can be combined in multiple different ways. As far as possible each module should be provided as a plugin availble through an entry point.

1. The first module with handle the extraction of interesting statistics from the database. This could in the future do the same thing but use the BED output directly for example.

  - The package will be built around a basic interface (API) to the Chanjo result SQL database. This API might in the future be released as a separate Python package (dependency).

  - What the most interesting metrics are and what format to store these metrics in needs to be defined.

2. Secondly the interesting data will be used by a report renderer. In case of the PDF, a Flask server will be used to fill in parts in a Jinja2 template that will be converted to a PDF via WeasyPrint.

  - Using a Flask server will enable an interesting use case where it can be used as part of a more complex analysis interface. To accomplish this, the report generator will be contained within a "Blueprint".

> I could be fun to investigate the future possibility of installing custom templates and/or style sheets. It's of cource perfectly possible to extract more data than is presented in any given template.

> Would it be possible to include Flask as an optional dependency? Does it matter?

### Components

#### Miner
The miner module includes a Flask-enables API class that can connect to a Chanjo database. It provides a number of useful methods that define interesting queries to ask the database.

  > It should be rather easy to define your own, more exotic queries :)

Builtin queries:
  - Samples
  - Average coverage/completeness across exome
  - Sex check/prediction based on coverage
  - Estimated extreme GC content performance

#### Interfaces
It might be possible to set up an object with all basic queries that are only ever executed when the interface loops over the query :)

### Configuration
The configuration of the plugin will be handled inside of the default ``chanjo.toml`` config file under the subsection ``[report]``. The values will show up in the Click context object. It's important that settings can be defined in as flexible manner as possible.

> In the future, it should be possible to define which what content content is displayed/included in the generated report.

### Usage
An early prototype required the server to be launched in a separate process while PDF generation ran in a different process. This wasn't an acceptable workflow, so it's important that the report is generated inside a single process with a single command.

### Installation
Especially the PDF generation requires a bunch of more or less obscure non-Python dependencies. This demands detailed and robust installations instructions. I will also set up a Vagrantfile to boot a fully functional box for development, testing, and demo purposes.

> Also because of the PDF complexity I hope to be able to set up PDF support with "extras_require" dependencies.


## Development
A "manage.py" file is used for development. The server can also be spun up using ``python -m chanjo_report`` but must then disable the reloader since it doesn't play nice with relative imports.

```bash
$ python manage.py runserver -r --debug --host=0.0.0.0
```

### Install
Start by installing Python on Ubuntu by following [these instructions](http://askubuntu.com/questions/101591/how-do-i-install-python-2-7-2-on-ubuntu).

Setup Ubuntu by installing non-Python dependencies.

```bash
$ sudo apt-get install libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

Clone the repository and install it for development.

```bash
$ git clone https://github.com/robinandeer/chanjo-report.git
$ cd chanjo-report
$ pip install --editable .
```


## Contributing
Anyone can help make this project better - read [CONTRIBUTION][CONTRIBUTION.md] to get started!


## License
MIT. See the [LICENSE](LICENSE) file for more details.


[fury-url]: http://badge.fury.io/py/chanjo-report
[fury-image]: https://badge.fury.io/py/chanjo-report.png

[travis-url]: https://travis-ci.org/robinandeer/chanjo-report
[travis-image]: https://travis-ci.org/robinandeer/chanjo-report.png?branch=develop
