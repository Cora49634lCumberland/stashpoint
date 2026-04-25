"""CLI commands for retention policy management."""

import click

from stashpoint.retention import (
    InvalidRetentionError,
    SnapshotNotFoundError,
    VALID_POLICIES,
    get_retention,
    list_retention,
    remove_retention,
    set_retention,
)


@click.group("retention")
def retention_cmd():
    """Manage snapshot retention policies."""


@retention_cmd.command("set")
@click.argument("snapshot")
@click.argument("policy", type=click.Choice(VALID_POLICIES))
@click.option("--value", type=int, default=None, help="Numeric value for the policy.")
def retention_set_cmd(snapshot: str, policy: str, value: int):
    """Set a retention policy on SNAPSHOT."""
    try:
        entry = set_retention(snapshot, policy, value)
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))
    except InvalidRetentionError as exc:
        raise click.ClickException(str(exc))
    msg = f"Retention policy '{policy}'"
    if "value" in entry:
        msg += f" (value={entry['value']})"
    click.echo(f"{msg} set on '{snapshot}'.")


@retention_cmd.command("get")
@click.argument("snapshot")
def retention_get_cmd(snapshot: str):
    """Show the retention policy for SNAPSHOT."""
    entry = get_retention(snapshot)
    if entry is None:
        click.echo(f"No retention policy set for '{snapshot}'.")
    else:
        policy = entry["policy"]
        value = entry.get("value")
        msg = f"policy={policy}"
        if value is not None:
            msg += f", value={value}"
        click.echo(f"{snapshot}: {msg}")


@retention_cmd.command("remove")
@click.argument("snapshot")
def retention_remove_cmd(snapshot: str):
    """Remove the retention policy from SNAPSHOT."""
    remove_retention(snapshot)
    click.echo(f"Retention policy removed from '{snapshot}'.")


@retention_cmd.command("list")
def retention_list_cmd():
    """List all retention policies."""
    policies = list_retention()
    if not policies:
        click.echo("No retention policies set.")
        return
    for name, entry in policies.items():
        policy = entry["policy"]
        value = entry.get("value")
        suffix = f" (value={value})" if value is not None else ""
        click.echo(f"{name}: {policy}{suffix}")
