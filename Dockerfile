###########
# BUILDER #
###########
FROM python:3.14-slim-bookworm AS python-builder

WORKDIR /app

# Create the virtualenv and install the exact locked chanjo-report dependencies from uv.lock
RUN pip install --no-cache-dir uv==0.13.4 && python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN UV_PROJECT_ENVIRONMENT=/venv uv sync --locked --no-dev --no-install-project

#########
# FINAL #
#########
FROM python:3.14-slim-bookworm

LABEL about.license="MIT License (MIT)"
LABEL about.tags="chanjo-report,chanjo,bam,NGS,coverage,python,flask"
LABEL about.home="https://github.com/Clinical-Genomics/chanjo-report"

# Install required libs
RUN apt-get update && apt-get install -y wkhtmltopdf

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

# Install the app itself, its dependencies are already in /venv
RUN pip install --no-cache-dir --no-deps --editable .

# Run the app as non-root user
USER worker
