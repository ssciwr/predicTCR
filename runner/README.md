# predicTCR Runner

The runner is a service that regularly polls the predicTCR web service for new jobs.

If a job is available, it

- downloads the input files for this job to a temporary directoy
- copies the contents of the scripts folder to this directory
- runs script.sh in this directory
- uploads result.zip from this directory to the web service

A JWT token is required to authenticate the runner with the web service,
which can be generated on the admin page of the website.

Any required conda dependencies should be added to env.yaml.

## Use

To use the runner, the JWT token and other settings below should be set in environment variables,
or in a file `.env` in the same location as the docker-compose.yml, e.g.:

```
PREDICTCR_API_URL="https://predictcr.lkeegan.dev/api"
PREDICTCR_JWT_TOKEN="abc123"
PREDICTCR_RUNNER_DATA_DIR="/data"
PREDICTCR_RUNNERS=4
PREDICTCR_POLL_INTERVAL=5
```

With this .env file, `docker compose up -d` will start 4 runner images in the background,
which poll the web service for new jobs every 5 seconds.

## Development

To test locally using Docker, you can directly talk to the backend service (this works because both docker-compose files use the same docker network)

```
PREDICTCR_RUNNER_API_URL="http://backend:8080/api"
PREDICTCR_RUNNER_JWT_TOKEN="" # you need to generate this using the admin page of your local instance
PREDICTCR_RUNNER_LOG_LEVEL=DEBUG
```
