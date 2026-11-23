"""Fixtures that build a real (SQLite) chanjo database from the demo files and serve it."""
from pathlib import Path

import pytest
from chanjo.load.link import link_elements
from chanjo.load.sambamba import load_transcripts
from chanjo.store.api import ChanjoDB

from chanjo_report.server.app import create_app
from chanjo_report.server.config import ProdConfig

DEMO = Path(__file__).parent / "fixtures" / "demo"
SAMPLES = ["sample1", "sample2", "sample3"]
AGRN_GENE_ID = 329


@pytest.fixture(scope="session")
def db_uri(tmp_path_factory):
    """URI of a chanjo database with 3 demo samples loaded and linked to demo transcripts."""
    uri = "sqlite:///" + str(tmp_path_factory.mktemp("chanjo") / "chanjo.sqlite3")
    chanjo_db = ChanjoDB(uri=uri)
    chanjo_db.set_up()

    with open(DEMO / "hgnc.min.bed", encoding="utf-8") as bed:
        linked = link_elements(bed)
    with chanjo_db.begin() as session:
        for model in linked.models:
            session.add(model)

    for name in SAMPLES:
        bed_path = DEMO / f"{name}.coverage.bed"
        with open(bed_path, encoding="utf-8") as bed:
            loaded = load_transcripts(bed, sample_id=None, group_id="test_group", source=str(bed_path))
        loaded.sample.name = name
        loaded.sample.group_name = "test_group"
        with chanjo_db.begin() as session:
            session.add(loaded.sample)
            for model in loaded.models:
                session.add(model)
    return uri


@pytest.fixture
def app(db_uri):
    class TestServerConfig(ProdConfig):
        SQLALCHEMY_DATABASE_URI = db_uri
        TESTING = True
        CHANJO_LANGUAGE = "en"
        CHANJO_PANEL_NAME = None
        CHANJO_PANEL = None

    return create_app(config=TestServerConfig)


@pytest.fixture
def client(app):
    return app.test_client()
