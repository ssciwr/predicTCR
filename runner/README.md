# predicTCR Runner

This will be a script or Docker image to do the Python+R analysis.

It needs to

- Regularly poll the predicTCR web service to ask if there is a sample that needs processing
- If one is available
  - claim the sample
  - download the input files
  - run the analysis
  - upload the results

Authentification can be done via a long-lived JWT token that admins can request online.

Deployment could be done with a Docker image and a docker-compose config.

Admin would set environment variables to provide

- path to model weights
- JWT token
