# predicTCR website deployment info

Some information on how to deploy the website.

## Production deployment

Production docker container images are automatically built by CI.

Before running them, the location of the data directory, SSL keys and secret key should be set
either in env vars or in a file `.env` in the same location as the docker compose.yml.

For example the current test deployment on heicloud looks like this:

```
PREDICTCR_DATA="/home/ubuntu/predicTCR/docker_volume"
PREDICTCR_SSL_CERT="/etc/letsencrypt/live/predictcr.com/fullchain.pem"
PREDICTCR_SSL_KEY="/etc/letsencrypt/live/predictcr.com/privkey.pem"
PREDICTCR_JWT_SECRET_KEY="abc123" # to generate a new secret key: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
```

### docker compose

To deploy the latest version on a virtual machine with docker compose installed,
download [docker-compose.yml](https://raw.githubusercontent.com/ssciwr/predicTCR/main/docker-compose.yml), then do

```
sudo docker compose pull && sudo docker compose up -d && sudo docker system prune -af
```

The same command can be used to update the running website to use the latest available docker images.

The current status of the running containers can be checked with

```
sudo docker compose ps
sudo docker compose logs
```

### SSL certificates

To generate SSL certificates for the domain `predictcr.com` from [Let's Encrypt](https://letsencrypt.org/) using [Certbot](https://certbot.eff.org/):

```
sudo docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d predictcr.com
```

The certificates needs renewing every three months, which can be done manually using the same command. To automatically renew once a week you can use cron, e.g. `sudo crontab -e`, then add the following line:

```
0 0 * * 0 docker run -it --rm -v/etc/letsencrypt:/etc/letsencrypt -v/var/www/certbot:/var/www/certbot certbot/certbot certonly --webroot --webroot-path /var/www/certbot/ -n -d predictcr.com
```

### Give users admin rights

To make an existing user with email `user@embl.de` into an admin, ssh into the VM, then

```
cd predicTCR
sudo sqlite3 docker_volume/predicTCR.db
sqlite> UPDATE user SET is_admin=true WHERE email='user@embl.de';
sqlite> .quit
```

### Visitor count

To get a count of the unique visitor IPs from the nginx logs:

```
sudo docker compose logs frontend --no-log-prefix | grep "GET" | awk '{print $1}' | sort | uniq | wc -l
```
