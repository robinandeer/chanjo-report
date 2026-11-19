![Example report (eng)](artwork/screenshot.png)

# Chanjo Report
Automatically generate basic coverage reports from Chanjo SQL databases. This plugin installs as a subcommand ("report") to the Chanjo command line interface.

## Usage
Chanjo Report supports a number of output formats: tabular, PDF, and HTML. To print a PDF coverage report for a group of samples "WGS-prep" do:

```bash
$ chanjo report --render pdf --group "WGS-prep" > ./coverage-report.pdf
```

## Features

### Supported output formats
Chanjo Reports multiple output formats:

  - tabular: easily parsable and pipeable
  - PDF: easily distributable (for humans)
  - HTML: easily deliverable on the web

### Supported languages (translations)
The coverage report (HTML/PDF) can be render is the following languages:

  - English
  - Swedish


## Motivation
We are using the output from Chanjo at Clincal Genomics to report success of sequencing across the exome based on coverage. Our customers, clinicians mostly, are specifically interested in knowing to what degree their genes of interest are covered by sequencing along with some intuitive overall coverage metrics. They want the output in PDF format to file it in their system.

As a side effect of finding it easiest to convert HTML to PDF, Chanjo Report has a built in Flask server that can be used to render reports dynamically and even be plugged into other Flask servers as a Blueprint.


### Installation

The latest version of Chanjo-report can be installed by cloning and installing the repository from Clinical Genomics github:

```bash
$ git clone https://github.com/Clinical-Genomics/chanjo-report.git
$ cd chanjo-report
$ pip install --editable .
```

### Demo instance with Docker

To run a local demo with Docker, ensure you have a Docker engine running.
If you do not have Docker set up, we can recommend Docker Desktop (https://www.docker.com/products/docker-desktop/).

Then use `make` with the repository `Makefile` to build and run:

```bash
make build
make setup
make report
```

Point your browser to `http://127.0.0.1:5000` and find the demo samples.

#### Comprehensive instructions

We provide a Dockerfile to run the server in a container. To run a demo instance of the server with a pre-populated database consisting of a case with 3 samples, clone the repository using the following commands:

 ```bash
 $ git clone https://github.com/Clinical-Genomics/chanjo-report.git
 $ cd chanjo-report
 ```

Then you could make use of the services present in the Docker-compose file following these 3 steps:

1. Build the images

    ```bash
    make build
    ```

2. Launch chanjo to create a populate the database with demo data

    ```bash
    make setup
    ```

3. Launch the chanjo-report server

     ```bash
     make report
     ```

A running instance of the server should now be available at the following url: http://localhost:5000/.

In order to generate a report containing all 3 demo samples, use the respective request args: http://localhost:5000/report?sample_id=sample1&sample_id=sample2&sample_id=sample3

Please be aware that if you are building and running the Dockerized version of chanjo-report, there might be **issues on `macOS` if your processor is Apple silicon** (or another `ARM64` based architecture).
In order to build the `chanjo-report` image in the `ARM64` architecture, you can set the environment variable `DOCKER_DEFAULT_PLATFORM`:

 ```bash
 export DOCKER_DEFAULT_PLATFORM=linux/amd64
make build
make setup
make report
```

## License
MIT. See the [LICENSE](LICENSE) file for more details.


## Contributing
Anyone can help make this project better - read [CONTRIBUTING](CONTRIBUTING.md) to get started!
