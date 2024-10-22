# predicTCR website

[![CI](https://github.com/ssciwr/predicTCR/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/predicTCR/actions/workflows/ci.yml)

The source code for the [predicTCR website](https://predictcr.lkeegan.dev/).

## Implemented features

### Users

Users of the site can

- sign up with a valid email address
- upload a sample to be analyzed
- see a list of their requested samples
- download the analysis results
- TODO automatically receive an email with their results

### Admins

Users with admin rights can additionally

- view and modify global settings
- create an API token for a runner to use
- view and modify registered users and runners
- view and download samples and results

## Runners

The analysis of the samples is done by runners, which

- are a separate service packaged as a docker container
- can be run on any machine with docker installed
- authenticate with the API using a token
- regularly check for new samples to analyze
- do sample analysis and upload the results

## Developer info

If you want to make changes to the code, see
[README_DEV](README_DEV.md)
for instructions on how to locally build make a test deployment of the website.

## Deployment info

For information on how to deploy the website see
[README_DEPLOYMENT](README_DEPLOYMENT.md).

## Acknowledgments

This project is based on the [SampleFlow](https://github.com/ssciwr/sample_flow) web service by the same authors.
