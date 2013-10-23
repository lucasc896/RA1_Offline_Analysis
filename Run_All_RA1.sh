#!/bin/sh


# Make Tex Tables
for i in {"2","3","all"}
do
   ./Prediction_RA1.py -n $i
done


# Make Uncorrected Tex Tables
for i in {"2","3","all"}
do
   ./Prediction_RA1.py -u $i
done

# Make Root Files
for i in {"2","3"}
do
   ./Prediction_RA1.py -r $i
done


# Make Closure Tests
for i in {"2","3","all","jetcat"}
do
   ./Prediction_RA1.py -c $i
done


