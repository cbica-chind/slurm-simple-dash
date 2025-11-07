#!/bin/bash

module load slurm

# this only works on infr4

cd /admin/centos7/httpd/var/www/html/slurm-load

source ~/Venvs/slurmdash/bin/activate
python3 /admin/bin/slurm-simple-dash.py
