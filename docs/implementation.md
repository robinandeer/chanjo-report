## Implementation
Chanjo Report is built using separate modules that can be combined in multiple different ways. As far as possible each module is provided as a plugin available through an entry point.

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
