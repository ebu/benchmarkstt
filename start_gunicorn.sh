#!/bin/sh
gunicorn -b :5000 --access-logfile - --error-logfile - conferatur.api.gunicorn
