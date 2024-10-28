#!/bin/sh

# This script will be ran by the runner in a temporary folder which contains the following user-provided input files:
#
#  - input.h5
#  - input.csv
#
# As well as the following empty folders where any results should be written:
#
#  - user_results/
#  - admin_results/
#

echo "Starting fake analysis..."

echo "Sleeping for 1 minute..."

sleep 60

echo "Writing placeholder user results..."

echo "Placeholder user results" > user_results/placeholder.txt

echo "Writing placeholder admin results..."

echo "Placeholder admin results" > admin_results/placeholder.txt

echo "done."
