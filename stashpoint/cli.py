"""CLI entry point for stashpoint."""

import click

from stashpoint.snapshot import capture, drop, list_snapshots, restore, show
from stashpoint.export import export_snapshot, import_snapshot


@click.group()
def cli() -> None:
    """stashpoint — manage named environment variable snapshots."""


@cli.command("save")
@click.argument("name")
@click.argument("keys", nargs=-1)
def save_cmd(name: str, keys: tuple) -> None:
    """Save current env vars as NAME. Optionally specify KEYS to capture."""
    key_list = list(keys) if keys else None
    capture(name, key_list)
    click.echo(f"Snapshot '{name}' saved.")


@cli.command("restore")
@click.argument("name")
def restore_cmd(name: str) -> None:
    """Restore env vars from snapshot NAME (prints export commands)."""
    result = restore(name)
    if result is None:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    for key, value in result.items():
        click.echo(f"export {key}={value}")


@cli.command("list")
def list_cmd() -> None:
    """List all saved snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots saved.")
    for name in names:
        click.echo(name)


@cli.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show variables stored in snapshot NAME."""
    data = show(name)
    if data is None:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)
    for key, value in data.items():
        click.echo(f"{key}={value}")


@cli.command("drop")
@click.argument("name")
def drop_cmd(name: str) -> None:
    """Delete snapshot NAME."""
    removed = drop(name)
    if removed:
        click.echo(f"Snapshot '{name}' dropped.")
    else:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)


@cli.command("export")
@click.argument("name")
@click.option("--output", "-o", default=None, help="Output file path.")
def export_cmd(name: str, output: str) -> None:
    """Export snapshot NAME to a portable JSON file."""
    try:
        path = export_snapshot(name, output)
        click.echo(f"Snapshot '{name}' exported to {path}.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cli.command("import")
@click.argument("file_path")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing snapshot.")
def import_cmd(file_path: str, overwrite: bool) -> None:
    """Import a snapshot from a JSON file."""
    try:
        name = import_snapshot(file_path, overwrite=overwrite)
        click.echo(f"Snapshot '{name}' imported from {file_path}.")
    except (FileNotFoundError, ValueError) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
