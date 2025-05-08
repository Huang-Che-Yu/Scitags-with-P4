#!/bin/bash


# if $1 is not in ["h1","h2","h3"] then exit
if [[ "$1" != "h1" && "$1" != "h2" && "$1" != "h3" ]]; then
  echo "This script should be run inside a Mininet host (h1, h2, h3)."
  exit 1
fi
echo "Entering Mininet host $1..."

sudo mnexec -a $(pgrep -f "mininet:$1") bash