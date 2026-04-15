"""CLI commands for comparing multiple snapshots side-by-side."""

import click
from stashpoint.compare import compare_snapshots, format_compare, SnapshotNotFoundError


@click.group("compare")
def compare_cmd():
    """Compare multiple snapshots side-by-side."""


@compare_cmd.command("run")
@click.argument("names", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output raw JSON.")
def compare_run_cmd(names, as_json):
    """Compare two or more snapshots by NAME.

    Example: stashpoint compare run dev staging prod
    """
    if len(names) < 2:
        click.echo("Error: provide at least two snapshot names.", err=True)
        raise SystemExit(1)

    try:
        result = compare_snapshots(list(names))
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if as_json:
        import json
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(format_compare(result))
