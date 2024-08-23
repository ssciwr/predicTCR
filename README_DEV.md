# predicTCR website developer info

Some information on how to locally build and deploy the website if you would like to make changes to the code.

## Run locally with docker compose

Pre-requisites:

- docker and docker compose
- you have created an SSL cert/key pair as described below

### SSL

SSL cert/key by default are assumed to exist as `cert.pem` and `key.pem`
in the folder where you run the docker compose command.
To point to different files, set the `PREDICTCR_SSL_CERT` and `PREDICTCR_SSL_KEY` environment variables.

For example to generate a cert/key pair on linux:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj '/CN=localhost'
```

To run the website locally in docker containers on your computer:

```sh
git clone https://github.com/ssciwr/predicTCR.git
cd predicTCR
docker compose up --build
```

### Database

The database will by default be stored in a `docker_volume` folder
in the folder where you run the docker compose command.
To modify this location, set the `PREDICTCR_DATA` environment variable.

### Secret Key

JWT tokens used for authentication are generated using a secret key.
This can be set using the `PREDICTCR_JWT_SECRET_KEY` environment variable.
If this is not set or is less than 16 chars, a new random secret key is generated when the server starts.

### URL

The website is then served at https://localhost/
Note that the SSL keys are self-signed keys and your browser will still warn about the site being insecure.

### User signup activation email

When you sign up for an account when running locally it will send an email (if port 25 is open) to whatever address you use.
If the port is blocked you can see the activation_token in the docker logs,
and activate your local account by going to `https://localhost/activate/<activation_token_from_logs>`
To make yourself an admin user, see the production deployment section below.

## Run locally with Python and npm

Clone the repo:

```sh
git clone https://github.com/ssciwr/predicTCR.git
cd predicTCR
```

Install and run the backend:

```sh
cd backend
pip install .
cd ..
predicTCR_server
```

Install and run the frontend:

```sh
cd frontend
npm install
npm run dev
```

The website is then served at http://localhost:5173/.
Note that email activation will not work without the postfix docker image.

## Implementation

### Backend

The backend is a Python Flask REST API, see [backend/README.md](backend/README.md) for more details.

### Frontend

The frontend is a vue.js app, see [frontend/README.md](frontend/README.md) for more details.

### Docker

Both the backend and the frontend have a Dockerfile,
and there is a docker compose file to coordinate them.
