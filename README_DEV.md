# predicTCR website developer info

Some information on how to locally build and serve the website if you would like to make changes to the code.
There are two ways to do this:

- docker
  - closer to production environment
  - but less convenient for development - you need to rebuild the image every time you make a change
- python/pnpm
  - further from production environment setup
  - but convenient for development - see changes immediately without having to rebuild or restart anything

## Run locally with docker

Requires docker and docker compose.

1. clone the repo:

```sh
git clone https://github.com/ssciwr/predicTCR.git
cd predicTCR
```

2. generate a SSL cert/key pair:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj '/CN=localhost'
```

3. build and run the website locally in docker containers on your computer:

```sh
docker compose up --build
```

The website is then served at https://localhost/
(note that the SSL keys are self-signed keys and your browser will still warn about the site being insecure.)

### Database

The database will by default be stored in a `docker_volume` folder
in the folder where you run the docker compose command.
To modify this location, set the `PREDICTCR_DATA` environment variable.

### Secret Key

JWT tokens used for authentication are generated using a secret key.
This can be set using the `PREDICTCR_JWT_SECRET_KEY` environment variable.
If this is not set or is less than 16 chars, a new random secret key is generated when the server starts.

### User signup activation email

When you sign up for an account when running locally it will send an email (if port 25 is open) to whatever address you use.
You can also see the activation_token in the docker logs,
and activate your local account by going to `https://localhost/activate/<activation_token_from_logs>`

### Make yourself an admin user

```
sudo sqlite3 docker_volume/predicTCR.db
sqlite> UPDATE user SET is_admin=true WHERE email='you@address.com';
sqlite> .quit
```

### Start a runner

In the runner directory, create a `.env` file with the following content:

```
PREDICTCR_RUNNER_API_URL="http://backend:8080/api"
PREDICTCR_RUNNER_JWT_TOKEN="" # you need to generate this using the admin page of your local instance
PREDICTCR_RUNNER_LOG_LEVEL=DEBUG
```

Then build and start the runner with:

```sh
docker compose up --build
```

## Run locally with Python and pnpm

Requires Python and [pnpm](https://pnpm.io/installation#using-a-standalone-script)

1. clone the repo:

```sh
git clone https://github.com/ssciwr/predicTCR.git
cd predicTCR
```

2. install and run the backend development server:

```sh
cd backend
pip install .
cd ..
predicTCR_server
```

3. install and run the frontend development server:

```sh
cd frontend
pnpm install
pnpm run dev
```

The website is then served at http://localhost:5173/.
Note that the email activation message will be written to the console instead of being sent by email.

4. install and run the runner:

```sh
cd runner
pip install .
predicTCR_runner
```
