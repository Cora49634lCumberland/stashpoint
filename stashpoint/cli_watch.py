"""CLI commands for snapshot drift watching."""

import click
from stashpoint.watch import check_drift, format_drift, SnapshotNotFoundError


@click.group("watch")
def watch_cmd():
    """Watch snapshots for environment drift."""
    pass


@watch_cmd.command("check")
@click.argument("name")
@click.option("--keys", "-k", multiple=True, help="Limit check to specific keys.")
@click.option("--quiet", "-q", is_flag=True, help="Exit 1 if drift found, no output.")
def watch_check_cmd(name: str, keys: tuple, quiet: bool):
    """Check if the current environment has drifted from a snapshot."""
    try:
        result = check_drift(name, list(keys) if keys else None)
    except SnapshotNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(2)

    if quiet:
        raise SystemExit(1 if result.has_drift else 0)

    click.echo(format_drift(result))
    if result.has_drift:
        raise SystemExit(1)
