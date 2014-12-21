#!/bin/sh

# Make Uncorrected Tex Tables
for i in {"2","3","5","all"}
do
#    ./Prediction_RA1.py -u $i
    ./Prediction_RA1.py -n $i
done
