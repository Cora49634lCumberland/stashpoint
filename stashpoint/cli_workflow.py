"""CLI commands for workflow management."""

from __future__ import annotations

import click

from stashpoint.workflow import (
    WorkflowAlreadyExistsError,
    WorkflowNotFoundError,
    SnapshotNotFoundError,
    append_step,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
)


@click.group("workflow")
def workflow_cmd() -> None:
    """Manage ordered snapshot workflows."""


@workflow_cmd.command("create")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
def workflow_create_cmd(name: str, steps: tuple[str, ...]) -> None:
    """Create a workflow NAME with ordered STEPS (snapshot names)."""
    try:
        result = create_workflow(name, list(steps))
        click.echo(f"Created workflow '{name}' with {len(result)} step(s).")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except WorkflowAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@workflow_cmd.command("delete")
@click.argument("name")
def workflow_delete_cmd(name: str) -> None:
    """Delete a workflow by NAME."""
    try:
        delete_workflow(name)
        click.echo(f"Deleted workflow '{name}'.")
    except WorkflowNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@workflow_cmd.command("show")
@click.argument("name")
def workflow_show_cmd(name: str) -> None:
    """Show steps of workflow NAME."""
    try:
        steps = get_workflow(name)
        click.echo(f"Workflow '{name}':")
        for i, step in enumerate(steps, 1):
            click.echo(f"  {i}. {step}")
    except WorkflowNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@workflow_cmd.command("list")
def workflow_list_cmd() -> None:
    """List all workflows."""
    workflows = list_workflows()
    if not workflows:
        click.echo("No workflows defined.")
        return
    for name, steps in workflows.items():
        click.echo(f"{name}: {' -> '.join(steps)}")


@workflow_cmd.command("append")
@click.argument("workflow_name")
@click.argument("snapshot_name")
def workflow_append_cmd(workflow_name: str, snapshot_name: str) -> None:
    """Append SNAPSHOT_NAME as the next step in WORKFLOW_NAME."""
    try:
        steps = append_step(workflow_name, snapshot_name)
        click.echo(f"Workflow '{workflow_name}' now has {len(steps)} step(s).")
    except (SnapshotNotFoundError, WorkflowNotFoundError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
