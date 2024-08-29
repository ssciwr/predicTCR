from __future__ import annotations
import click
from predicTCR_server import create_app
from predicTCR_server.logger import get_logger
from flask_cors import CORS
import predicTCR_server.email


@click.command()
@click.option("--host", default="localhost", show_default=True)
@click.option("--port", default=8080, show_default=True)
@click.option("--data-path", default=".", show_default=True)
def main(host: str, port: int, data_path: str):
    app = create_app(data_path=data_path)
    # local development server: enable CORS on all routes for all origins
    CORS(app)
    # local development server: log email messages instead of sending them
    logger = get_logger()
    predicTCR_server.email._send_email_message = lambda email_message: logger.info(
        email_message
    )
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
