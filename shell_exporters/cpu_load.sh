#!/bin/sh

# CPU Load
# Print CPU load in percentage to STDout
top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}'