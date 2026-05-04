#!/bin/bash

if [ -d "../whats_new/" ]; then
    if [ -f "../whats_new/expiry.txt" ]; then
        expiry_time=$(<"../whats_new/expiry.txt")
        now=$(date +%s);
        echo $expiry_time;
        echo $now;
        if [ "$expiry_time" -lt "$now" ]; then
            rm -r '../whats_new/'
            echo 'BYE';
        fi
        echo 'HI';
    fi
fi