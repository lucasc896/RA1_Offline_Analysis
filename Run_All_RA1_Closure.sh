#!/bin/sh

# Make Closure Tests

for i in {"1","2","3","4","all","jetcat"}
do
   ./Prediction_RA1.py -c $i
done



