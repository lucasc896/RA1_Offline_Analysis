#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(description ='Produce RA1 Results')
parser.add_argument('-c',help= 'Make RA1 Closure Tests, Choose all, 2 or 3 or jetcat',nargs='+', type =str)
parser.add_argument('-u',help= 'Make RA1 Tables Uncorrected Yields',action="store_true")
parser.add_argument('-m',help= 'Make RA1 MC Normalisation Tables',action="store_true")
parser.add_argument('-r',help= 'Make RA1 Root Files, Choose all, 2 or 3',nargs='+',type=str)
parser.add_argument('-n',help= 'Make RA1 Tables, Choose all, 2 or 3',nargs='+',type =str)
parser.add_argument('-t',help= 'Make Template fitting',choices = ['had','muon']) 
parser.add_argument('-j',help= 'Set jet categories fit to default 2,3,4,>=5', nargs='+',type = str,default=["2","3","4","5"])
args = parser.parse_args()

from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime
import array  #, ast
import math as m
from plottingUtils import *
from NumberCruncher import *
from time import strftime

settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],  #HT Bins
  "bins":["200","275","325","375","475","575","675","775","875","975","1075"],  #HT Bins
  "plots":["AlphaT_",],  # Histogram that Yields are taken from
  "AlphaTSlices":["0.55_20"], # AlphaT Slices
  "Lumo":19.255, # Luminosity in fb
  "Multi_Lumi":{'Had':18.583,'Muon':19.255,'DiMuon':19.255,'Photon':20.34},  # Different Luminosity per sample, used when SplitLumi = True
  "Analysis":"8TeV" # Differentiate between 7 and 8 TeV analysis i.e. uses alphaT cut in lowest two bins if 7TeV is selected
      }


def ensure_dir(dir):
        try: os.makedirs(dir)
        except OSError as exc: pass

def Directory_Maker():
     
    print "\n Making RA1 Directories"
    folder_options = {'NormalisationTables':args.m,'ClosureTests':args.c,'TexFiles':args.n,'TexFiles':args.n,'RootFiles':args.r,'Templates':args.t  }
    folders = []

    for key,fi in folder_options.iteritems():
        print folder_options
        if fi != None and fi != False: folders.append(key)

    dir_stamp = "RA1_Documents_"+strftime("%d_%b")
    ensure_dir(dir_stamp)
    base = os.getcwd()
    os.chdir(dir_stamp)
    owd = os.getcwd()
    for path in folders:

       print "Making Dir %s"%path
       ensure_dir(path)
       os.chdir(owd)
'''
Sample Dictionary Instructions
eg "nMuon":("./May_11_root_Files/Muon_Data","btag_two_OneMuon_","Data","Muon"),
if n at start of name entry then the file is data and will no be scaled to luminosity.
first argument is path to root file
second argument is prefix to ht bin. i.e OneMuon_275_325
third argument is data/mc type, i.e. Data, WJets250 - MC relating to the binned WJets 250-300 HT sample
fourth argument is sample Type, Had/DiMuon/Muon. 

the only thing that will have to be changed is the second argument depending on wether you are running btag multiplicity/baseline
'''
btag_more_than_three_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_morethanthree_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanthree_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanthree_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_morethanthree_Photon_","Data","Photon"),

    }

btag_more_than_three_uncorrected_samples = {

    "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_morethanthree_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","btag_morethanthree_","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","btag_morethanthree_","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","btag_morethanthree_","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","btag_morethanthree_","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","btag_morethanthree_","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","btag_morethanthree_","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanthree_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_morethanthree_OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_morethanthree_OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_morethanthree_OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_morethanthree_OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_morethanthree_OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_morethanthree_OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanthree_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_morethanthree_DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_morethanthree_DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_morethanthree_DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_morethanthree_DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_morethanthree_DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_morethanthree_DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","btag_morethanthree_Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_morethanthree_Photon_","Data","Photon"),

    }

btag_two_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_two_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
     "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_two_Photon_","Data","Photon"),
    }


btag_more_than_zero_normalisation = {

    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanzero_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     "mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanzero_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     "mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_morethanzero_Photon_","Data","Photon"),

    }


btag_two_normalisation = {

     "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     "mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     "mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_two_Photon_","Data","Photon"),
   
 
    }


btag_two_uncorrected_samples = {

    "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_two_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","btag_two_","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","btag_two_","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","btag_two_","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","btag_two_","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","btag_two_","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","btag_two_","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_two_OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_two_OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_two_OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_two_OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_two_OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_two_OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_two_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_two_DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_two_DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_two_DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_two_DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_two_DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_two_DiMuon_","DY","DiMuon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_two_Photon_","Data","Photon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),

    }

btag_one_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_one_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_one_OneMuon_","Data","Muon"),
    "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_one_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_one_Photon_","Data","Photon"),

    }

btag_one_uncorrected_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_one_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","btag_one_","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","btag_one_","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","btag_one_","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","btag_one_","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","btag_one_","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","btag_one_","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_one_OneMuon_","Data","Muon"),
    "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_one_OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_one_OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_one_OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_one_OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_one_OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_one_OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_one_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_one_DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_one_DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_one_DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_one_DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_one_DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_one_DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","btag_one_Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_one_Photon_","Data","Photon"),

    }

btag_zero_normalisation = {
     
     "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     "mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     "mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "nPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_zero_Photon_","Data","Photon"),
   

 
    }


btag_zero_samples = {
     
     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_zero_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
     "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_zero_Photon_","Data","Photon"),

    }

btag_zero_uncorrected_samples = {
     
     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_zero_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","btag_zero_","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","btag_zero_","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","btag_zero_","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","btag_zero_","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","btag_zero_","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","btag_zero_","DY","Had"),
     "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_zero_OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_zero_OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_zero_OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_zero_OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_zero_OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_zero_OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_zero_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_zero_DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_zero_DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_zero_DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_zero_DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_zero_DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_zero_DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","btag_zero_Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_zero_Photon_","Data","Photon"),

    }

btag_three_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_three_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_three_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_three_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_three_Photon_","Data","Photon"),

    }

btag_three_uncorrected_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_three_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","btag_three_","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","btag_three_","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","btag_three_","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","btag_three_","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","btag_three_","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","btag_three_","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_three_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_three_OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_three_OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_three_OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_three_OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_three_OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_three_OneMuon_","DY","Muon"),
     "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_three_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","btag_three_DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","btag_three_DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","btag_three_DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","btag_three_DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","btag_three_DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","btag_three_DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","btag_three_Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_three_Photon_","Data","Photon"),

    }

btag_more_than_zero_samples = {

    "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_morethanzero_","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanzero_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanzero_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_morethanzero_Photon_","Data","Photon"),

    }

btag_more_than_one_samples = {

     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","btag_morethanone_","Data","Had"),
    
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanone_OneMuon_","Data","Muon"),
     "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","btag_morethanone_DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","btag_morethanzero_Photon_","Data","Photon"),

    }

inclusive_samples = {
     
     "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","","Data","Had"),
     "mcHadW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_WJets","","WJets","Had"),
     "mcHadttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_TTbar","","TTbar","Had"),
     "mcHadzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Zinv","","Zinv","Had"),
     "mcHadsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_SingleTop","","SingleTop","Had"),
     #"mcHaddiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DiBoson","","DiBoson","Had"),
     "mcHadDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_DY","","DY","Had"),
    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","OneMuon_","Data","Muon"),
    "mcMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","OneMuon_","WJets","Muon"),
     "mcMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","OneMuon_","TTbar","Muon"),
     "mcMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","OneMuon_","Zinv","Muon"),
     "mcMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
     #"mcMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
     "mcMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","DiMuon_","Data","DiMuon"),
     "mcDiMuonW1":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_WJets","DiMuon_","WJets","DiMuon"),
     "mcDiMuonttbar":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
     "mcDiMuonzinv":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
     "mcDiMuonsingt":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
     #"mcDiMuondiboson":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
     "mcDiMuonDY":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_DY","DiMuon_","DY","DiMuon"),
     "mcPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_MC","Photon_","Photon","Photon"),
     "ncPhoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Photon_Data","Photon_","Data","Photon"),

    }

calc_file = {
     "mchadz2":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Z2.root","Had_Z2",""),
     "mchadz0":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Z0.root","Had_Z0",""),
     "mcmuonz2":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Z2.root","Muon_Z2","OneMuon_"),
     "mcmuonz0":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Z0.root","Muon_Z0","OneMuon_"),
     "mcdimuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Z0.root","DiMuon","DiMuon_"),
     "mcphoton":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Z0.root","Photon",""),

}

#============== File Lists for template fitting ==============

had_template_samples = {

    "nHad":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Data","","Data","Had"),
     "mcHadComb":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_MC_Template","","MC","Had"),
     "mcHadZ0":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Z0","","Z0","Had"),
     "mcHadZ2":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Had_Z2","","Z2","Had"),

    }

muon_template_samples = {

    "nMuon":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Data","OneMuon_","Data","Muon"),
     "mcMuonComb":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_MC_Template","OneMuon_","MC","Muon"),
     "mcMuonZ0":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Z0_v2","OneMuon_","Z0","Muon"),
     "mcMunZ2":("../MASTER_ROOT_FILES/Root_Files_ISR_PU_Applied/Muon_Z2","OneMuon_","Z2","Muon"),

    }



if __name__=="__main__":


  Directory_Maker() 

  if args.t :
     WP = ["Loose","Medium","Tight"]
     settings["dirs"] = ["275_325","325_375","Template_375"]
     template_ = {'had':had_template_samples,'muon':muon_template_samples}
     
     for point in WP:
        Number_Extractor(settings,template_[args.t],"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="all",Template=args.j,Do_sys = "True",Working_Point = point)


  if args.m :

    #settings["dirs"] = ["150_200"] + settings["dirs"]
    #settings["bins"] = ["150"] + settings["bins"]
    print settings
    print" ==================  \n Making MC Clamping Normalisation Yields \n ====================  \n"
    Number_Extractor(settings,btag_zero_normalisation,"Zero_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="2",RunOption = "MCNormalisation")
    Number_Extractor(settings,btag_zero_normalisation,"Zero_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="all",RunOption = "MCNormalisation")
    Number_Extractor(settings,btag_more_than_zero_normalisation,"More_Than_Zero_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="3",RunOption = "MCNormalisation")
    Number_Extractor(settings,btag_two_normalisation,"Two_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="all",RunOption ="MCNormalisation")
    Number_Extractor(settings,btag_two_normalisation,"Two_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="3",RunOption ="MCNormalisation")


  if args.n : 
   
    print" ==================  \n Making Tables Formula Yields \n ====================  \n"
   
    for j in args.n:
       print " ========= Jet Mult %s ======== " %j
       Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)
       Number_Extractor(settings,btag_zero_samples,"Zero_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)
       Number_Extractor(settings,btag_one_samples,"One_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)
       Number_Extractor(settings,btag_two_samples,"Two_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)
       Number_Extractor(settings,btag_three_samples,"Three_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)
       Number_Extractor(settings,btag_more_than_three_samples,"More_Than_Three_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category=j)

  if args.u : 

    print" ==================  \n Making Tables Uncorrected Yields \n ====================  \n"
    settings["plots"] = ["Number_Btags_"]
    
    for j in ["all","2","3"]:
      print " ========= Jet Mult %s ======== " %j
      Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      #Number_Extractor(settings,btag_zero_uncorrected_samples,"Zero_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      #Number_Extractor(settings,btag_one_uncorrected_samples,"One_btag",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      #Number_Extractor(settings,btag_two_uncorrected_samples,"Two_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      #Number_Extractor(settings,btag_three_uncorrected_samples,"Three_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      #Number_Extractor(settings,btag_more_than_three_uncorrected_samples,"More_Than_Three_btag",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category= j)

  if args.r : 
 
    print" ==================  \n Making Root Files \n ====================  \n"
    for j in args.r:
      print " ======  Jet Mult %s  ========= \n"%j
      Number_Extractor(settings,btag_two_samples,"Two_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_one_samples,"One_btag",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_zero_samples,"Zero_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_three_samples,"Three_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_more_than_three_samples,"More_Than_Three_btag",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)

  if args.c : 
        
    print" ==================  \n Making Closure Tests \n ====================  \n"
    settings["AlphaTSlices"] = ["0.55_20","0.01_10"]

    if "jetcat" in args.c:
      print " ======= Making Jetcategory closure tests ========"
      CLOSURE_TESTS = []
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="2")
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="3")
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="all")
      Jad_Compute(settings,CLOSURE_TESTS,classic ="False",Lumo = settings["Lumo"],jetcat = "True")

    for j in args.c:
      if "jetcat" in args.c : continue
      print " ======  Jet Mult %s  ========= \n"%j
      CLOSURE_TESTS = []
      Number_Extractor(settings,btag_two_samples,"Two_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_one_samples,"One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Number_Extractor(settings,btag_zero_samples,"Zero_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_more_than_zero_samples,"More_Than_Zero_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_more_than_one_samples,"More_Than_One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Jad_Compute(settings,CLOSURE_TESTS,Lumo = settings["Lumo"],classic="False",jetcat = "False",jet_mult = "_%s"%j)

   

 
