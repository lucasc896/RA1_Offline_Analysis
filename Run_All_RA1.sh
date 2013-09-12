#!/bin/sh

# Make Closure Tests
for i in {"2","3","all","jetcat"}
do
   ./Prediction_RA1.py -c $i
done

# Make Tex Tables
for i in {"2","3"}
do
   ./Prediction_RA1.py -n $i
done

comment1(){
# Make Root Files
for i in {"2","3"}
do
   ./Prediction_RA1.py -r $i
done
}
