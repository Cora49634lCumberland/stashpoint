"""CLI commands for snapshot scheduling."""

import click
from stashpoint.schedule import (
    set_schedule,
    remove_schedule,
    get_schedule,
    list_schedules,
    SnapshotNotFoundError,
    ScheduleNotFoundError,
    VALID_INTERVALS,
)
from stashpoint.storage import load_snapshots


@click.group("schedule")
def schedule_cmd():
    """Manage automatic snapshot schedules."""


@schedule_cmd.command("set")
@click.argument("name")
@click.argument("interval", type=click.Choice(VALID_INTERVALS))
def schedule_set_cmd(name, interval):
    """Set a schedule interval for a snapshot."""
    try:
        set_schedule(name, interval, snapshots=load_snapshots())
        click.echo(f"Scheduled '{name}' to capture {interval}.")
    except SnapshotNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@schedule_cmd.command("remove")
@click.argument("name")
def schedule_remove_cmd(name):
    """Remove the schedule for a snapshot."""
    try:
        remove_schedule(name)
        click.echo(f"Removed schedule for '{name}'.")
    except ScheduleNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@schedule_cmd.command("get")
@click.argument("name")
def schedule_get_cmd(name):
    """Show the schedule for a snapshot."""
    entry = get_schedule(name)
    if entry is None:
        click.echo(f"No schedule set for '{name}'.")
    else:
        click.echo(f"{name}: {entry['interval']}")


@schedule_cmd.command("list")
def schedule_list_cmd():
    """List all scheduled snapshots."""
    data = list_schedules()
    if not data:
        click.echo("No schedules configured.")
    else:
        for name, entry in data.items():
            click.echo(f"{name}: {entry['interval']}")
