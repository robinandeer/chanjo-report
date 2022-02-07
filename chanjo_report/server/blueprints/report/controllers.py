from chanjo.store.models import Sample
from flask import session

from chanjo_report.server.constants import LEVELS

from .utils import keymetrics_rows, samplesex_rows, transcripts_rows


def report_contents(request):
    """Check args or form provided by user request and prepare contents for report or pdf enrpoints
    Args:
        request(flask.Request)

    Returns:
        data(dict)
    """

    sample_ids = request.args.getlist("sample_id") or request.form.getlist("sample_id")
    raw_gene_ids = request.args.get("gene_ids") or request.form.get("gene_ids")
    gene_ids = []
    if raw_gene_ids:
        session["all_genes"] = raw_gene_ids
        gene_ids = [gene_id.strip() for gene_id in raw_gene_ids.split(",")]
    else:
        if request.method == "GET" and session.get("all_genes"):
            gene_ids = [gene_id.strip() for gene_id in session.get("all_genes").split(",")]

    int_gene_ids = set()
    gene_id_errors = set()
    for gene_id in gene_ids:
        try:
            int_gene_ids.add(int(gene_id))
        except ValueError:
            gene_id_errors.add(gene_id)

    int_gene_ids = list(int_gene_ids)

    level = int(request.args.get("level") or request.form.get("level") or 10)
    extras = {
        "panel_name": (request.args.get("panel_name") or request.form.get("panel_name")),
        "level": level,
        "gene_ids": int_gene_ids,
        "show_genes": any([request.args.get("show_genes"), request.form.get("show_genes")]),
    }
    samples = Sample.query.filter(Sample.id.in_(sample_ids))
    case_name = request.args.get("case_name") or request.form.get("case_name")
    sex_rows = samplesex_rows(sample_ids)
    metrics_rows = keymetrics_rows(sample_ids, genes=int_gene_ids)
    tx_rows = transcripts_rows(sample_ids, genes=int_gene_ids, level=level)

    data = dict(
        sample_ids=sample_ids,
        samples=samples,
        case_name=case_name,
        sex_rows=sex_rows,
        levels=LEVELS,
        extras=extras,
        metrics_rows=metrics_rows,
        tx_rows=tx_rows,
        gene_id_errors=gene_id_errors,
    )
    return data
