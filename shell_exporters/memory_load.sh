#!/bin/sh

# Memory Load
# Print Memory load in percentage to STDout
free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }'