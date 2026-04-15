"""CLI commands for snapshot merging."""

import click
from stashpoint.merge import merge_snapshots, get_merge_conflicts, SnapshotNotFoundError


@click.command("merge")
@click.argument("sources", nargs=-1, required=True)
@click.option("--into", "target", required=True, help="Name for the merged snapshot.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite the target snapshot if it already exists.",
)
@click.option(
    "--strategy",
    type=click.Choice(["last-wins", "first-wins"], case_sensitive=False),
    default="last-wins",
    show_default=True,
    help="How to resolve key conflicts between sources.",
)
def merge_cmd(sources: tuple[str, ...], target: str, overwrite: bool, strategy: str) -> None:
    """Merge SOURCES snapshots into a single snapshot named TARGET.

    Keys that appear in multiple sources are resolved according to --strategy.
    """
    try:
        merged = merge_snapshots(
            list(sources),
            target_name=target,
            overwrite=overwrite,
            strategy=strategy,
        )
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Merged {len(sources)} snapshot(s) into '{target}' ({len(merged)} keys, strategy={strategy})."
    )


@click.command("merge-conflicts")
@click.argument("sources", nargs=-1, required=True)
def merge_conflicts_cmd(sources: tuple[str, ...]) -> None:
    """Show keys that conflict across SOURCES snapshots before merging."""
    try:
        conflicts = get_merge_conflicts(list(sources))
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not conflicts:
        click.echo("No conflicts found across the given snapshots.")
        return

    click.echo(f"Conflicts found ({len(conflicts)} key(s)):")
    for key, values in sorted(conflicts.items()):
        formatted_values = ", ".join(repr(v) for v in values)
        click.echo(f"  {key}: [{formatted_values}]")
