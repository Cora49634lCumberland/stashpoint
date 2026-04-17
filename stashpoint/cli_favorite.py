import click
from stashpoint.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    SnapshotNotFoundError,
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
)


@click.group("favorite")
def favorite_cmd():
    """Manage favorite snapshots."""


@favorite_cmd.command("add")
@click.argument("name")
def favorite_add_cmd(name):
    """Mark a snapshot as a favorite."""
    try:
        favorites = add_favorite(name)
        click.echo(f"Added '{name}' to favorites. Favorites: {', '.join(favorites)}")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except FavoriteAlreadyExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@favorite_cmd.command("remove")
@click.argument("name")
def favorite_remove_cmd(name):
    """Remove a snapshot from favorites."""
    try:
        favorites = remove_favorite(name)
        remaining = ', '.join(favorites) if favorites else '(none)'
        click.echo(f"Removed '{name}' from favorites. Remaining: {remaining}")
    except FavoriteNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@favorite_cmd.command("list")
def favorite_list_cmd():
    """List all favorite snapshots."""
    favorites = list_favorites()
    if not favorites:
        click.echo("No favorites set.")
    else:
        for name in favorites:
            click.echo(name)


@favorite_cmd.command("check")
@click.argument("name")
def favorite_check_cmd(name):
    """Check if a snapshot is a favorite."""
    if is_favorite(name):
        click.echo(f"'{name}' is a favorite.")
    else:
        click.echo(f"'{name}' is not a favorite.")
