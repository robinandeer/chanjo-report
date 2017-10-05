# -*- coding: utf-8 -*-
import click

from chanjo_report.interfaces import html, pdf


@click.command()
@click.option('-r', '--render', type=click.Choice(['html', 'pdf']), default='html')
@click.option('-l', '--language', type=click.Choice(['en', 'sv']))
@click.option('-d', '--debug', is_flag=True)
@click.pass_context
def report(context, render, language, debug):
    """Generate a coverage report from Chanjo SQL output."""
    # get uri + dialect of Chanjo database
    if context.obj['database'] is None:
        click.echo('database URI not found')
        context.abort()

    # set the custom option
    context.obj['report'] = dict(language=language, debug=debug)

    if render == 'html':
        html.render_html(context.obj)
    else:
        pdf.render_pdf(context.obj)
