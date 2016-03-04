# -*- coding: utf-8 -*-
from pkg_resources import load_entry_point

import click

from .utils import list_interfaces
from chanjo.store import ChanjoAPI
from chanjo.store.txmodels import BASE

ROOT_PACKAGE = __package__.split('.')[0]


@click.command()
@click.option('-r', '--render', type=click.Choice(list_interfaces()),
              default='html')
@click.option('-s', '--samples', type=str, multiple=True)
@click.option('-g', '--group', type=str)
@click.option('-l', '--language', type=click.Choice(['en', 'sv']))
@click.option('-p', '--gene-id', multiple=True,
              help='list of gene ids to filter on')
@click.option('-n', '--panel-name', type=str, help='name of gene panel')
@click.pass_context
def report(context, render, language, samples, group, gene_id, panel_name):
    """Generate a coverage report from Chanjo SQL output."""
    # get uri + dialect of Chanjo database
    uri = context.obj.get('database')

    # set the custom option
    context.obj.set('report.panel', gene_id)
    context.obj.set('report.samples', samples)
    context.obj.set('report.group', group)
    context.obj.set('report.language', language)

    # guess name of gene panel unless explicitly set
    if gene_id:
        context.obj.set('report.panel_name', panel_name)

    # create instance of Chanjo API "Miner"
    api = ChanjoAPI(uri, base=BASE)

    # determine which render method to use and initialize it
    render_method = load_entry_point(ROOT_PACKAGE, 'chanjo_report.interfaces',
                                     render)

    # run the render_method and print the result to STDOUT
    click.echo(render_method(api, options=context.obj))
