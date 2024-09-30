from __future__ import annotations

import click
import logging
from .runner import Runner


@click.command()
@click.option("--api-url", type=str)
@click.option("--jwt-token", type=str)
@click.option("--poll-interval", type=int, default=5, show_default=True)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="Log level",
    show_default=True,
    show_choices=True,
)
def main(api_url, jwt_token, poll_interval, log_level):
    logging.basicConfig(
        level=log_level, format="%(levelname)s %(module)s.%(funcName)s :: %(message)s"
    )
    runner = Runner(api_url, jwt_token, poll_interval)
    runner.start()


if __name__ == "__main__":
    main(auto_envvar_prefix="PREDICTCR")
