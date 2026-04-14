"""CLI entry point for stashpoint."""

import sys
import click

from stashpoint.snapshot import capture, drop, list_snapshots, restore, show


@click.group()
def cli():
    """stashpoint — manage named environment variable snapshots."""


@cli.command("save")
@click.argument("name")
@click.option("--keys", "-k", multiple=True, help="Specific env var keys to capture.")
def save_cmd(name, keys):
    """Capture current environment as a named snapshot."""
    env_vars = capture(name, list(keys) if keys else None)
    click.echo(f"✔ Saved snapshot '{name}' with {len(env_vars)} variable(s).")


@cli.command("restore")
@click.argument("name")
@click.option("--no-overwrite", is_flag=True, default=False,
              help="Skip keys already set in the environment.")
def restore_cmd(name, no_overwrite):
    """Restore a named snapshot into the current environment."""
    try:
        env_vars = restore(name, overwrite=not no_overwrite)
        click.echo(f"✔ Restored snapshot '{name}' ({len(env_vars)} variable(s)).")
    except KeyError as e:
        click.echo(f"✖ {e}", err=True)
        sys.exit(1)


@cli.command("list")
def list_cmd():
    """List all saved snapshots."""
    names = list_snapshots()
    if not names:
        click.echo("No snapshots found.")
    else:
        for name in names:
            click.echo(f"  • {name}")


@cli.command("show")
@click.argument("name")
def show_cmd(name):
    """Display the contents of a named snapshot."""
    try:
        env_vars = show(name)
        for key, value in sorted(env_vars.items()):
            click.echo(f"  {key}={value}")
    except KeyError as e:
        click.echo(f"✖ {e}", err=True)
        sys.exit(1)


@cli.command("drop")
@click.argument("name")
def drop_cmd(name):
    """Delete a named snapshot."""
    if drop(name):
        click.echo(f"✔ Deleted snapshot '{name}'.")
    else:
        click.echo(f"✖ Snapshot '{name}' not found.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
