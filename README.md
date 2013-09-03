Directory contains all files necessary to run RA1 offline analysis. 

Can be loosely called a framework, but in reality is a poor implementation of python classes. However it all works, but feel free to take, adapt and improve on this in future.

Prediction RA1 - Config file, file paths to file directories are set here


Run_All...    - bash scripts to automatically produce all usual required RA1 outputs


NumberCruncher - Produces a dictionary of all yields, errors for all processes and sorts them into relevant 'sub' dictionaries for insertion in tables or closure tests

Closure Tests - Where closure tests are defined and then produced

Btag_Calculation - This is where the RA1 formula method is implemented. Yields are formulaically calculated through jet flavour content of each process. 

Calculation_Template - Not used in RA1 analysis, used for producing template method to estimate yields at high b-tag multiplicities.

Fit_MHT_MET - Absoultely budget way to determine linear fit for MHT_MET sidebands
