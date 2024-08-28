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
PREDICTCR_API_URL="https://predictcr.iwr.uni-heidelberg.de/api"
PREDICTCR_JWT_TOKEN="abc123"
PREDICTCR_RUNNER_DATA_DIR="/data"
PREDICTCR_REPLICAS=2
PREDICTCR_POLL_INTERVAL=5
```

`docker compose up -d` will then start `PREDICTCR_REPLICAS` runner images in the background.
