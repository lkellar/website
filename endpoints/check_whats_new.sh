#!/bin/bash
# needs to be run in this directory

if [ -d "../whats_new/" ]; then
    if [ -f "../whats_new/expiry.txt" ]; then
        expiry_time=$(<"../whats_new/expiry.txt");
        now=$(date +%s);
        if [ "$expiry_time" -lt "$now" ]; then
            rm ../whats_new/*;
        fi
        touch ../whats_new/index.html;
    fi
fi