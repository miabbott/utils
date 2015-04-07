#!/bin/bash

if [ -z "$1" ]; then
        LOOP="10"
else
        LOOP=$1
fi

if [ -z "$2" ]; then
        DELAY="10"
else
        DELAY="$2"
fi

UPGRADE='atomic host upgrade'
FAILED_FILE='/var/qe/atomic_upgrade_failed'

if [ -e "$FAILED_FILE" ]; then
    rm $FAILED_FILE
fi

for l in $(seq $LOOP); do
        echo "Attempting upgrade iteration $l of $LOOP with a delay of $DELAY seconds"
        timeout --signal=SIGINT $DELAY $UPGRADE
        UPGRADE_RV=$?
        if [ "$UPGRADE_RV" -ne 124 ] && [ "$UPGRADE_RV" -ne 0 ]; then
                echo "ERROR! The 'atomic host upgrade' command did not exit successfully or via SIGINT"
                echo "ERROR! The reported exit status was: $UPGRADE_RV"
                touch /var/qe/atomic_upgrade_failed
                break
        fi
        sleep 5
        echo -e "\n"
done
