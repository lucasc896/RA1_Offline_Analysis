#!/bin/sh


# Make Tex Tables
for i in {"1","2","3","4","all"}
do
   ./Prediction_RA1.py -u $i
done

