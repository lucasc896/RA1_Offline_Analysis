#!/bin/sh

# Make Closure Tests

for i in {"2","3","all","jetcat"}
do
   ./Prediction_RA1.py -c $i
done



