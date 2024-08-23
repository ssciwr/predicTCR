# predicTCR website

[![CI](https://github.com/ssciwr/predicTCR/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/predicTCR/actions/workflows/ci.yml)

The source code for the [predicTCR website](https://predictcr.iwr.uni-heidelberg.de/).

## Implemented features

### Users

Users of the site can

- sign up with a valid email address
- request a sample, optionally providing a reference sequence
- see a list of their requested samples
- download their reference sequences
- download full analysis data
- automatically receive an email with their results

### Admins

Users with admin rights can additionally

- see a list of all users
- see a list of all requested samples and results
- change the site settings
  - set which day of the week sample submission closes
  - set number of plate rows/cols
  - add/remove running options
- download a zipped tsv of requests from the current week
  - this includes the reference sequences as fasta files
- upload a zipfile with successful analysis results to be sent to the user
- upload unsuccessful analysis result status to be sent to the user

### REST API

Admins can also generate an API token,
then do all of the above programatically using
the provided REST API:

- [api_examples.ipynb](https://github.com/ssciwr/predicTCR/blob/main/notebooks/api_examples.ipynb)

## Developer info

If you want to make changes to the code, see
[README_DEV](README_DEV.md)
for instructions on how to locally build make a test deployment of the website.

## Deployment info

For information on how to deploy the website see
[README_DEPLOYMENT](README_DEPLOYMENT.md).

## Acknowledgments

This project is based on the [SampleFlow](https://github.com/ssciwr/sample_flow) web service by the same authors.
