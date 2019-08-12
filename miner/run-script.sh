#!/bin/sh

# ensure only one instance of script is running
# https://unix.stackexchange.com/a/48511
me="$(basename "$0")";
running=$(ps h -C "$me" | grep -wv $$ | wc -l);

echo $me >> /app/log/app-name

if [[ $running -gt 1 ]]; then
    exit
fi

# load environment
# https://superuser.com/a/1240860
set -a; source /etc/environment; set +a;

python3 /app/app.py
