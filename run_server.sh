#!/bin/sh
#
if [ -n "$1" ]; then
    PORT="$1"
else
    PORT="12345"
fi

python -m src.server.main -p "$PORT"
