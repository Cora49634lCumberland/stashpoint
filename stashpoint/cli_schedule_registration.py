from stashpoint.cli_schedule import schedule_cmd


def register(cli):
    cli.add_command(schedule_cmd)
