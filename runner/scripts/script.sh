#!/bin/sh

# This script runs the analysis and puts the output in result.zip

echo "Starting fake analysis..."

echo "Sleeping for 1 minute..."

sleep 60

ls > result.zip

echo "done."

# Rscript preprocess.R

# python predict.py
