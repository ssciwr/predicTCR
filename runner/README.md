# predicTCR Runner

The runner is a service packaged as a Docker container that regularly polls the predicTCR web service for new jobs.

If a job is available, it

- downloads the input h5/csv files for this job to a temporary directoy
- creates these empty folders in this directory:
  - /user_results
  - /trusted_user_results
  - /admin_results
- copies the contents of the `PREDICTCR_RUNNER_SCRIPT_DIR` folder to this directory
- runs script.sh in this directory
- uploads each results directory as a zip file to the web service

A JWT token is required to authenticate the runner with the web service,
which can be generated on the admin page of the website.

The docker image has R and Python dependencies pre-installed.

## Use

To use the runner, download the [docker-compose.yml](docker-compose.yml) file.

Then create a file named `.env` in the same location as the docker-compose.yml,
with the JWT token, the location of your script folder, and other desired settings, e.g.:

```
PREDICTCR_API_URL="https://predictcr.com/api"
PREDICTCR_JWT_TOKEN="abc123"
PREDICTCR_RUNNER_SCRIPT_DIR="./script"
PREDICTCR_RUNNER_JOBS=4
PREDICTCR_MAXPOLL_INTERVAL=60
```

With this .env file, `docker compose up -d` will start 4 runner images in the background, which will copy the files
from the `script` folder to do the processing.

To update to the latest runner docker images: `docker compose pull && docker compose up -d`

## Development

To test locally using Docker, you can directly talk to the backend service (this works because both docker-compose files use the same docker network)

```
PREDICTCR_RUNNER_API_URL="http://backend:8080/api"
PREDICTCR_RUNNER_JWT_TOKEN="" # you need to generate this using the admin page of your local instance
PREDICTCR_RUNNER_LOG_LEVEL=DEBUG
```
