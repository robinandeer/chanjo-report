###########
# BUILDER #
###########
FROM clinicalgenomics/python3.8-venv:1.0 AS python-builder

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Install chanjo-report dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#########
# FINAL #
#########
FROM python:3.8-slim

LABEL about.license="MIT License (MIT)"
LABEL about.tags="chanjo-report,chanjo,bam,NGS,coverage,python,python3.8,flask"
LABEL about.home="https://github.com/Clinical-Genomics/chanjo-report"

# Install required libs
RUN apt-get update && apt-get install -y \
  libcairo2 libpango-1.0-0 libpangocairo-1.0-0

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
RUN echo export PATH="/venv/bin:\$PATH" > /etc/profile.d/venv.sh

# Create a non-root user to run commands
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --shell /usr/sbin/nologin --create-home worker

# Copy virtual environment from builder
COPY --chown=worker:worker --from=python-builder /venv /venv

# Move to workdir and copy app
WORKDIR /home/worker/app
COPY --chown=worker:worker . /home/worker/app

# Install the app
RUN pip install --editable .

# Run the app as non-root user
USER worker
