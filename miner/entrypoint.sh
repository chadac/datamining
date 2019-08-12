#!/bin/sh

printenv > /etc/environment

crontab -l > cron
echo "$MIN $HOUR $DAY $MONTH $WEEK /home/run-script.sh" > cron
crontab cron
rm cron

crond -f -L /dev/stdout
