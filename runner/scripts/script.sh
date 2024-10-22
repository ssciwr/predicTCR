#!/bin/sh

# This script runs the analysis and puts the output in result.zip

echo "Starting fake analysis..."

echo "Sleeping for 5 minutes..."

sleep 300

ls > result.zip

echo "done."

# Rscript preprocess.R

# python predict.py
