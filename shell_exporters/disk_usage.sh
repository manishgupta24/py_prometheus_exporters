#!/bin/sh

# Disk Usage
# Print Disk Usage in percentage to STDout
df -h | awk '$NF=="/"{printf "%s", $5}' | tr --delete %
