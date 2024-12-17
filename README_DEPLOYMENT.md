# predicTCR website deployment info

Some information on how to deploy the website.

## Production deployment

Production docker container images are automatically built by CI.
To deploy the latest version on a virtual machine with docker compose installed,
download [docker-compose.yml](https://raw.githubusercontent.com/ssciwr/predicTCR/main/docker-compose.yml), then do

```
sudo docker compose pull
sudo docker compose up -d
```

The location of data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker compose.yml.

For example the current test deployment on heicloud looks like this:

```
PREDICTCR_DATA="/home/ubuntu/predicTCR/docker_volume"
PREDICTCR_SSL_CERT="/etc/letsencrypt/live/predictcr.com/fullchain.pem"
PREDICTCR_SSL_KEY="/etc/letsencrypt/live/predictcr.com/privkey.pem"
PREDICTCR_JWT_SECRET_KEY="abc123" # to generate a new secret key: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
```

The current status of the containers can be checked with

```
sudo docker compose ps
sudo docker compose logs
```

### SSL certificate

To generate SSL certificates for domain `domain.com` from [Let's Encrypt](https://letsencrypt.org/) using [Certbot](https://certbot.eff.org/):

```
sudo docker run -it --rm --name certbot -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" -p80:80 -p443:443 certbot/certbot certonly -d domain.com
```

choose option 1, certs will be saved to `/etc/letsencrypt/live/domain.com/`

They need renewing every three months, to update the certificate manually:

```
sudo docker compose down
sudo docker run -it --rm --name certbot -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" -p80:80 -p443:443 certbot/certbot renew
sudo docker compose up -d
```

### Give users admin rights

To make an existing user with email `user@embl.de` into an admin, ssh into the VM, then

```
cd predicTCR
sudo sqlite3 docker_volume/predicTCR.db
sqlite> UPDATE user SET is_admin=true WHERE email='user@embl.de';
sqlite> .quit
```
