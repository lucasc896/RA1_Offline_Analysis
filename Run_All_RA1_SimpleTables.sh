#!/bin/sh


# Make Tex Tables
for i in {"2","3","all"}
do
   ./Prediction_RA1.py -u $i
done

