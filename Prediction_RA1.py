#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(description ='Produce RA1 Results')
parser.add_argument('-c',help= 'Make RA1 Closure Tests, Choose all, 2 or 3 or jetcat',nargs='+', type =str)
parser.add_argument('-u',help= 'Make RA1 Tables Uncorrected Yields', nargs='+', type =str)
parser.add_argument('-m',help= 'Make RA1 MC Normalisation Tables',action="store_true")
parser.add_argument('-r',help= 'Make RA1 Root Files, Choose all, 2 or 3',nargs='+',type=str)
parser.add_argument('-n',help= 'Make RA1 Tables, Choose all, 2 or 3',nargs='+',type =str)
parser.add_argument('-t',help= 'Make Template fitting',choices = ['had','muon']) 
parser.add_argument('-j',help= 'Set jet categories fit to default 2,3,4,>=5', nargs='+',type = str,default=["2","3","4","5"])
parser.add_argument('-d',help= 'For debug use', action="store_true")
args = parser.parse_args()

import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
import array
import math as m
from time import strftime
from plottingUtils import *
from NumberCruncher import *
from time import strftime, time, sleep
from run_details import this_run

r.gROOT.SetBatch(r.kTRUE)

baseTime = time()

settings = {
  "dirs":["200_275","275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"],  #HT Bins
  "bins":["200","275","325","375","475","575","675","775","875","975","1075"],  #HT Bins
  "plots":["AlphaT_",],  # Histogram that Yields are taken from
  "AlphaTSlices":["0.55_50", "0.56_50", "0.57_50", "0.58_50", "0.59_50", "0.60_50"][:1], # AlphaT Slices, WARNING: this fucks up Formula Method!!
  "Lumo":this_run()["had_lumi"], # Luminosity in fb
  "Multi_Lumi":{'Had':this_run()["had_lumi"],'Muon':this_run()["mu_lumi"],'DiMuon':this_run()["mu_lumi"],'Photon':this_run()["ph_lumi"]},  # Different Luminosity per sample, used when SplitLumi = True
  "sb_corrs":{'WJets':this_run()["wj_corr"], "Photon":this_run()["dy_corr"], "Zinv":this_run()["dy_corr"], "DY":this_run()["dy_corr"], "Top":this_run()["tt_corr"]},
  "Analysis":"8TeV", # Differentiate between 7 and 8 TeV analysis i.e. uses alphaT cut in lowest two bins if 7TeV is selected
  "MHTMET":["False", "True"][1]
      }

'''
Set some variables for file access
'''

print "\n>> Opening directory:", this_run()["path_name"]
sleep(3)

rootDirectory = "../../" + this_run()["path_name"]
rootDirectoryNorm = rootDirectory

data_run_suf = ["", "_Run2012A", "_Run2012B", "_Run2012C", "_Run2012D", "_Run2012ABC", "_Run2012BC"][0]

def ensure_dir(dir):
        try:
            os.makedirs(dir)
        except OSError as exc:
            pass

def Directory_Maker():
     
    print "\n Making RA1 Directories"
    folder_options = {'NormalisationTables':args.m,'ClosureTests':args.c,'TexFiles':args.n,'TexFilesuncorrected':args.u,'RootFiles':args.r,'Templates':args.t,'TexFiles':args.d  }
    folders = []

    for key,fi in folder_options.iteritems():
        # print folder_options
        if fi != None and fi != False: 
          if key == "TexFilesuncorrected": folders.append("TexFiles")
          else: folders.append(key)

    dir_stamp = "RA1_Documents_"+strftime("%d_%b")
    ensure_dir(dir_stamp)
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
third argument is data/mc type, i.e. Data, WJets - MC relating to the SM Process
fourth argument is sample Type, Had/DiMuon/Muon. 

the only thing that will have to be changed is the second argument depending on wether you are running btag multiplicity/baseline
'''
btag_more_than_three_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_morethanthree_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanthree_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanthree_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_morethanthree_Photon_","Data","Photon"),

    }

btag_more_than_three_uncorrected_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_morethanthree_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","btag_morethanthree_","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","btag_morethanthree_","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","btag_morethanthree_","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","btag_morethanthree_","SingleTop","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","btag_morethanthree_","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanthree_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","btag_morethanthree_OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","btag_morethanthree_OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","btag_morethanthree_OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_morethanthree_OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_morethanthree_OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","btag_morethanthree_OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanthree_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","btag_morethanthree_DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","btag_morethanthree_DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","btag_morethanthree_DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_morethanthree_DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_morethanthree_DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","btag_morethanthree_DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","btag_morethanthree_Photon_","Photon","Photon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_morethanthree_Photon_","Data","Photon"),
    }

btag_two_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_two_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_two_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_two_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_two_Photon_","Data","Photon"),
    }


btag_more_than_zero_normalisation = {

    "nMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_morethanzero_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectoryNorm+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectoryNorm+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_morethanzero_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectoryNorm+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectoryNorm+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectoryNorm+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectoryNorm+"/Photon_Data"+data_run_suf,"btag_morethanzero_Photon_","Data","Photon"),
    }

btag_more_than_one_normalisation = {

    "nMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_morethanone_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectoryNorm+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectoryNorm+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_morethanone_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectoryNorm+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectoryNorm+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectoryNorm+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectoryNorm+"/Photon_Data"+data_run_suf,"btag_morethanone_Photon_","Data","Photon"),
    }



btag_two_normalisation = {

    "nMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_two_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectoryNorm+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectoryNorm+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_two_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectoryNorm+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectoryNorm+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectoryNorm+"/Photon_MC","Photon_","Photon","Photon"),
    "nPhoton":(rootDirectoryNorm+"/Photon_Data"+data_run_suf,"btag_two_Photon_","Data","Photon"),
    }


btag_two_uncorrected_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_two_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","btag_two_","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","btag_two_","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","btag_two_","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","btag_two_","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","btag_two_","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","btag_two_","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_two_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","btag_two_OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","btag_two_OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","btag_two_OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_two_OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_two_OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","btag_two_OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_two_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","btag_two_DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","btag_two_DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","btag_two_DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_two_DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_two_DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","btag_two_DiMuon_","DY","DiMuon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_two_Photon_","Data","Photon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),

    }

btag_one_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_one_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_one_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_one_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_one_Photon_","Data","Photon"),

    }

btag_one_uncorrected_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_one_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","btag_one_","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","btag_one_","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","btag_one_","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","btag_one_","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","btag_one_","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","btag_one_","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_one_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","btag_one_OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","btag_one_OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","btag_one_OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_one_OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_one_OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","btag_one_OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_one_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","btag_one_DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","btag_one_DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","btag_one_DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_one_DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_one_DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","btag_one_DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","btag_one_Photon_","Photon","Photon"),
    "nPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_one_Photon_","Data","Photon"),

    }

btag_zero_normalisation = {
     
    "nMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_zero_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectoryNorm+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectoryNorm+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectoryNorm+"/Muon_Data"+data_run_suf,"btag_zero_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectoryNorm+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectoryNorm+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectoryNorm+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectoryNorm+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectoryNorm+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectoryNorm+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectoryNorm+"/Photon_MC","Photon_","Photon","Photon"),
    "nPhoton":(rootDirectoryNorm+"/Photon_Data"+data_run_suf,"btag_zero_Photon_","Data","Photon"),

    }


btag_zero_samples = {
     
    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_zero_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_zero_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_zero_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_zero_Photon_","Data","Photon"),

    }

btag_zero_uncorrected_samples = {
     
    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_zero_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","btag_zero_","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","btag_zero_","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","btag_zero_","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","btag_zero_","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","btag_zero_","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","btag_zero_","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_zero_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","btag_zero_OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","btag_zero_OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","btag_zero_OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_zero_OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_zero_OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","btag_zero_OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_zero_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","btag_zero_DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","btag_zero_DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","btag_zero_DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_zero_DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_zero_DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","btag_zero_DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","btag_zero_Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_zero_Photon_","Data","Photon"),

    }

btag_three_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_three_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_three_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_three_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_three_Photon_","Data","Photon"),

    }

btag_three_uncorrected_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_three_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","btag_three_","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","btag_three_","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","btag_three_","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","btag_three_","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","btag_three_","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","btag_three_","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_three_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","btag_three_OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","btag_three_OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","btag_three_OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_three_OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_three_OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","btag_three_OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_three_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","btag_three_DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","btag_three_DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","btag_three_DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","btag_three_DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","btag_three_DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","btag_three_DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","btag_three_Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_three_Photon_","Data","Photon"),

    }

btag_more_than_zero_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_morethanzero_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanzero_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanzero_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_morethanzero_Photon_","Data","Photon"),

    }

btag_more_than_one_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"btag_morethanone_","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanone_OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"btag_morethanone_DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"btag_morethanzero_Photon_","Data","Photon"),

    }

inclusive_samples = {
     
    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"","Data","Had"),
    "mcHadW1":(rootDirectory+"/Had_WJets","","WJets","Had"),
    "mcHadttbar":(rootDirectory+"/Had_TTbar","","TTbar","Had"),
    "mcHadzinv":(rootDirectory+"/Had_Zinv","","Zinv","Had"),
    "mcHadsingt":(rootDirectory+"/Had_SingleTop","","SingleTop","Had"),
    "mcHaddiboson":(rootDirectory+"/Had_DiBoson","","DiBoson","Had"),
    "mcHadDY":(rootDirectory+"/Had_DY","","DY","Had"),
    # "mcSMS":(rootDirectory+"/Had_T2cc","","T2cc","Had"),
    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"OneMuon_","Data","Muon"),
    "mcMuonW1":(rootDirectory+"/Muon_WJets","OneMuon_","WJets","Muon"),
    "mcMuonttbar":(rootDirectory+"/Muon_TTbar","OneMuon_","TTbar","Muon"),
    "mcMuonzinv":(rootDirectory+"/Muon_Zinv","OneMuon_","Zinv","Muon"),
    "mcMuonsingt":(rootDirectory+"/Muon_SingleTop","OneMuon_","SingleTop","Muon"),
    "mcMuondiboson":(rootDirectory+"/Muon_DiBoson","OneMuon_","DiBoson","Muon"),
    "mcMuonDY":(rootDirectory+"/Muon_DY","OneMuon_","DY","Muon"),
    "nDiMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"DiMuon_","Data","DiMuon"),
    "mcDiMuonW1":(rootDirectory+"/Muon_WJets","DiMuon_","WJets","DiMuon"),
    "mcDiMuonttbar":(rootDirectory+"/Muon_TTbar","DiMuon_","TTbar","DiMuon"),
    "mcDiMuonzinv":(rootDirectory+"/Muon_Zinv","DiMuon_","Zinv","DiMuon"),
    "mcDiMuonsingt":(rootDirectory+"/Muon_SingleTop","DiMuon_","SingleTop","DiMuon"),
    "mcDiMuondiboson":(rootDirectory+"/Muon_DiBoson","DiMuon_","DiBoson","DiMuon"),
    "mcDiMuonDY":(rootDirectory+"/Muon_DY","DiMuon_","DY","DiMuon"),
    "mcPhoton":(rootDirectory+"/Photon_MC","Photon_","Photon","Photon"),
    "ncPhoton":(rootDirectory+"/Photon_Data"+data_run_suf,"Photon_","Data","Photon"),

    }

"""
These are the files used to calculate the btag,mistag rate per HT bin for each of the different processes.

Z0 - WJets, DY, Zinv
Z2 - TTbar, DiBoson, SingleTop

"""


calc_file = {
     "mchadz2":(rootDirectory+"/Had_Z2.root","Had_Z2",""),
     "mchadz0":(rootDirectory+"/Had_Z0.root","Had_Z0",""),
     "mcmuonz2":(rootDirectory+"/Muon_Z2.root","Muon_Z2","OneMuon_"),
     "mcmuonz0":(rootDirectory+"/Muon_Z0.root","Muon_Z0","OneMuon_"),
     "mcdimuon":(rootDirectory+"/Muon_Z0.root","DiMuon","DiMuon_"),
     "mcphoton":(rootDirectory+"/Had_Z0.root","Photon",""),

}

#============== File Lists for template fitting ==============

had_template_samples = {

    "nHad":(rootDirectory+"/Had_Data"+data_run_suf,"","Data","Had"),
     "mcHadComb":(rootDirectory+"/Had_MC_Template","","MC","Had"),
     "mcHadZ0":(rootDirectory+"/Had_Z0","","Z0","Had"),
     "mcHadZ2":(rootDirectory+"/Had_Z2","","Z2","Had"),

    }

muon_template_samples = {

    "nMuon":(rootDirectory+"/Muon_Data"+data_run_suf,"OneMuon_","Data","Muon"),
     "mcMuonComb":(rootDirectory+"/Muon_MC_Template","OneMuon_","MC","Muon"),
     "mcMuonZ0":(rootDirectory+"/Muon_Z0_v2","OneMuon_","Z0","Muon"),
     "mcMunZ2":(rootDirectory+"/Muon_Z2","OneMuon_","Z2","Muon"),

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

    settings["dirs"] = ["150_200"] + settings["dirs"]
    settings["bins"] = ["150"] + settings["bins"]
    #settings["dirs"] = ["275_325","325_375","375_475","475_575","575_675","675_775","775_875","875_975","975_1075","1075"]  #HT Bins
    #settings["bins"] = ["275","325","375","475","575","675","775","875","975","1075"]  #HT Bins

    
    print" ==================  \n Making MC Clamping Normalisation Yields \n ====================  \n"
    Number_Extractor(settings,btag_zero_normalisation,"Zero_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="2",RunOption = "MCNormalisation")
    Number_Extractor(settings,btag_zero_normalisation,"Zero_btags",Triggers = "True",AlphaT="True",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="2",RunOption = "MCNormalisation")
    #Number_Extractor(settings,btag_zero_normalisation,"Zero_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="all",RunOption = "MCNormalisation")
    #Number_Extractor(settings,btag_more_than_zero_normalisation,"More_Than_Zero_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="3",RunOption = "MCNormalisation")
    #Number_Extractor(settings,btag_more_than_one_normalisation,"More_Than_One_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="2",RunOption = "MCNormalisation")
    #Number_Extractor(settings,btag_more_than_one_normalisation,"More_Than_One_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="3",RunOption = "MCNormalisation")
    #Number_Extractor(settings,btag_more_than_one_normalisation,"More_Than_One_btag",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="all",RunOption = "MCNormalisation")

    Number_Extractor(settings,btag_two_normalisation,"Two_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="all",RunOption ="MCNormalisation")
    #Number_Extractor(settings,btag_two_normalisation,"Two_btags",Triggers = "True",AlphaT="False",Calculation=calc_file,Stats = "False",Split_Lumi = "True",Analysis_category="3",RunOption ="MCNormalisation")


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

  if args.u:

    print" ==================  \n Making Tables Uncorrected Yields \n ====================  \n"
    
    for j in args.u:
      print " ========= Jet Mult %s ======== " %j
      Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_zero_uncorrected_samples,"Zero_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_one_uncorrected_samples,"One_btag",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_two_uncorrected_samples,"Two_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_three_uncorrected_samples,"Three_btags",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_more_than_three_uncorrected_samples,"More_Than_Three_btag",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category= j)

  if args.r:
 
    print" ==================  \n Making Root Files \n ====================  \n"
    for j in args.r:
      print " ======  Jet Mult %s  ========= \n"%j
      Number_Extractor(settings,btag_two_samples,"Two_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_one_samples,"One_btag",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_zero_samples,"Zero_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_three_samples,"Three_btags",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)
      Number_Extractor(settings,btag_more_than_three_samples,"More_Than_Three_btag",Triggers = "False",AlphaT="False",Calculation=calc_file,Stats = "True",Split_Lumi = "True",Analysis_category =j)

  if args.c:
        
    print" ==================  \n Making Closure Tests \n ====================  \n"
    settings["AlphaTSlices"] = ["0.55_20","0.01_10"]

    if "jetcat" in args.c:
      print " ======= Making Jetcategory closure tests ========"
      CLOSURE_TESTS = []
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="1")
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="2")
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="3")
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="all")
      Jad_Compute(settings,CLOSURE_TESTS,classic ="False",Lumo = settings["Lumo"],jetcat = "True")

    if "sitv" in args.c:
      print " ======= Making SITV closure tests ========"
      CLOSURE_TESTS = []
      Number_Extractor(settings,btag_more_than_one_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="1")
      Number_Extractor(settings,btag_more_than_one_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="2")
      Number_Extractor(settings,btag_more_than_one_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="3")
      Number_Extractor(settings,btag_more_than_one_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category="all")
      print CLOSURE_TESTS
      exit()
      Jad_Compute(settings,CLOSURE_TESTS,classic ="False",Lumo = settings["Lumo"],jetcat = "False", sitv = "True")

    for j in args.c:
      if "jetcat" in args.c : continue
      if "sitv" in args.c : continue
      print " ======  Jet Mult %s  ========= \n"%j
      CLOSURE_TESTS = []
      Number_Extractor(settings,btag_two_samples,"Two_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_one_samples,"One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Number_Extractor(settings,btag_zero_samples,"Zero_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_more_than_zero_samples,"More_Than_Zero_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j)
      Number_Extractor(settings,btag_more_than_one_samples,"More_Than_One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=j) 
      Jad_Compute(settings,CLOSURE_TESTS,Lumo = settings["Lumo"],classic="False",jetcat = "False",jet_mult = "_%s"%j)



  if args.d:
    print" ==================  \n In DEBUG mode \n ====================  \n"

    settings["AlphaTSlices"] = ["0.55_20","0.01_10"]
    # CLOSURE_TESTS = []
    # jetmulti = "1"
    # Number_Extractor(settings,btag_two_samples,"Two_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti)
    # Number_Extractor(settings,btag_one_samples,"One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti) 
    # Number_Extractor(settings,btag_zero_samples,"Zero_btags",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti)
    # Number_Extractor(settings,btag_more_than_zero_samples,"More_Than_Zero_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti)
    # Number_Extractor(settings,btag_more_than_one_samples,"More_Than_One_btag",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti) 
    # Number_Extractor(settings,inclusive_samples,"Inclusive",c_file = CLOSURE_TESTS,Closure = "True",Triggers = "True",AlphaT="True",Calculation=calc_file,Split_Lumi = "True",Analysis_category=jetmulti) 
    # Jad_Compute(settings,CLOSURE_TESTS,Lumo = settings["Lumo"],classic="False",jetcat = "False",jet_mult = "_"+jetmulti)
    Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="1")
    # Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="2")
    # Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="3")
    # Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="4")
    # Number_Extractor(settings,inclusive_samples,"Inclusive",Triggers = "True",AlphaT="False",Split_Lumi = "True",Analysis_category="All")
  print "\n", "*"*52
  print "\tTotal Analysis time: ", time()-baseTime
  print "*"*52
    
