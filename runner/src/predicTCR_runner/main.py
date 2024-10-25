from __future__ import annotations

import click
import logging
from .runner import Runner


@click.command()
@click.option("--api-url", type=str)
@click.option("--jwt-token", type=str)
@click.option("--max-poll-interval", type=int, default=60, show_default=True)
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
def main(api_url, jwt_token, max_poll_interval, log_level):
    logging.basicConfig(
        level=log_level, format="%(levelname)s %(module)s.%(funcName)s :: %(message)s"
    )
    logging.info("Starting predict TCR runner")
    logging.info(f"  - api_url={api_url}")
    logging.info(f"  - max_poll_interval={max_poll_interval}s")
    logging.info(f"  - log_level={log_level}")
    runner = Runner(api_url, jwt_token, max_poll_interval)
    runner.start()


def main_env_vars():
    main(auto_envvar_prefix="PREDICTCR")


if __name__ == "__main__":
    main()
