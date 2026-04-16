"""CLI commands for searching snapshots."""

import click
from stashpoint.search import search_snapshots, NoSnapshotsFoundError


@click.group("search")
def search_cmd():
    """Search snapshots by key or value patterns."""


@search_cmd.command("run")
@click.option("--key", "-k", default=None, help="Glob pattern to match against keys.")
@click.option("--value", "-v", default=None, help="Glob pattern to match against values.")
def search_run_cmd(key, value):
    """Search snapshots by key and/or value glob pattern."""
    if not key and not value:
        raise click.UsageError("Provide at least --key or --value.")

    try:
        results = search_snapshots(key_pattern=key, value_pattern=value)
    except NoSnapshotsFoundError as e:
        click.echo(str(e))
        return

    if not results:
        click.echo("No matches found.")
        return

    for snapshot_name, matches in results.items():
        click.echo(f"[{snapshot_name}]")
        for k, v in matches.items():
            click.echo(f"  {k}={v}")
