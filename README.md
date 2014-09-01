# Chanjo Report [![PyPI version][fury-image]][fury-url] [![Build Status][travis-image]][travis-url]
Chanjo Report automatically renders a coverage report from Chanjo ouput.

The interface is available primarily as a subcommand to "chanjo".

The plugin will be able to serve HTML and PDF output to a local browser. It will be built with Flask Blueprints in mind to also be an easy block to plug into an existing server setup.

The configuration of the plugin will be handled inside of the default ``chanjo.toml`` config file under the subsection ``[report]``. The generated report can be configured as to what content is displayed/included.

The PDF/HTML generation is built on Jinja2, Flask, and WeasyPrint technologies.

The package will be built around a basic interface to the Chanjo result SQL database. This API might in the future be released as a separate Python package (dependency).

Is it possible to include Flask as an optional dependency? Does it matter? The goal should be to issue a *single* command to output a finished PDF report.

A "manage.py" file is used for development. The server can also be spun up using "python chanjo_report" but must then disable the reloader since it doesn't place nice with relative imports.

```bash
$ python manage.py runserver -r --debug --host=0.0.0.0
```


## Features

```python
# alternatively, if the PDF does not have a matching HTML page:
@app.route('/hello_<name>.raw')
def hello_raw(name):
  # make a PDF straight from HTML in a string
  html = render_template('hello.html', name=name)
  return render_pdf(HTML(string=html))
```


## Install for development
sudo apt-get install libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

```bash
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
