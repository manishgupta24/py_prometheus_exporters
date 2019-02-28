#!/bin/sh

# Originial Commands

# Memory Usage
MEM_USE="$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')"
# Disk Usage
DISK_USE="$(df -h | awk '$NF=="/"{printf "%s", $5}' | tr --delete %)"
# CPU Load
CPU_LOAD="$(top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}')"

echo '{"cpu_gauge":'${CPU_LOAD}', "disk_gauge":'${DISK_USE}', "memory_gauge":'${MEM_USE}'}'