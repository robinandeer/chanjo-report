FROM python:3.8-slim

LABEL base_image="python:3.8-slim"
LABEL about.license="MIT License (MIT)"
LABEL about.tags="chanjo-report,chanjo,bam,NGS,coverage,alpine,python,python3.8,flask"
LABEL about.home="https://github.com/Clinical-Genomics/chanjo-report"

# Install required libs
RUN apt-get update && apt-get install -y \
  libcairo2 libpango-1.0-0 libpangocairo-1.0-0

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install the app
RUN pip install --editable .

# Create and switch to a new non-root user
RUN useradd worker
RUN chown worker:worker -R /home/worker
USER worker

#ENTRYPOINT ["chanjo", "report"]
#CMD ["--help"]
