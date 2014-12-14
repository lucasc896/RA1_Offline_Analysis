#!/usr/bin/env python
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime
from optparse import OptionParser
import array, ast
from math import *
from plottingUtils import *

r.gROOT.SetBatch(r.kTRUE)

class Jad_Compute(object):
  
  def __init__(self,settings,dict_list,Lumo = "",classic = "",jetcat = "",jet_mult = ""):

    print "\n\n Now Computing Jad Translation Plots\n\n"
    self.Lumo = Lumo
    self.Classic = classic
    self.JetCat = jetcat
    self.settings = settings
    self.jetmult = jet_mult
    self.dict_list = dict_list

    # switch to turn on the combination of bins above 375
    self.combine_high_bins = [False, True][0]

    if self.combine_high_bins:
      print ">>> Warning: combining upper bins in closure test plots."

    self.MakeVectors(dict_list)

      
  def MakeVectors(self,dict_list):
    r.gROOT.ProcessLine(".L tdrstyle.C")
    r.setstyle()
    r.gROOT.SetBatch(True)
    r.gStyle.SetErrorX(0.)
    r.gStyle.SetEndErrorSize(0.)
    r.gStyle.SetOptStat(1)
    r.gStyle.SetOptFit(1)
    self.c1= r.TCanvas("Yields", "Yields",0,0,900,600)
    self.c1.SetHighLightColor(2)
    self.c1.SetFillColor(0)
    self.c1.SetBorderMode(0)
    self.c1.SetBorderSize(2)
    self.c1.SetTickx(1)
    self.c1.SetTicky(1)
    self.c1.SetFrameBorderMode(0)
    self.c1.SetFrameBorderMode(0)
    self.c1.cd(1)
    
    self.axis = [ ] 
    self.axis_dir = self.settings["bins"]
    for j in self.settings["bins"]: self.axis.append(int(j))
    self.axis.append(int(self.settings["bins"][-1]) + 100)
    '''
    Closure Tests are defined here. Follow same format to add additional tests and add it to test_dicts

    Jetcat is used to look at differences between jet multiplcity cateogires. This is passed from Prediction RA1
    Classic is not really used anymore

    option reduce, fits the line from 375 upwards. Used if making closure tests with photons as they are no lower 3 bins.  Just change the option in the box accordingly.
    '''

    if self.JetCat == "True":
      print "In JetSplit mode"
      test_1 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True", 'plot_title':"#mu + jets (2,3 Jets) #rightarrow #mu + jets (Gr4 Jets)",'scale':None,'reduce':"False",'file_name':'JetCat_muon_to_muon','spread':'False' } 
      test_2 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#mu#mu + jets (2,3 Jets) #rightarrow #mu#mu + jets (Gr4 Jets) ",'scale':None,'reduce':"False",'file_name':'JetCat_dimuon_to_dimuon','spread':'False' }
      test_3 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#gamma + jets (2,3 Jets) #rightarrow #gamma + jets (Gr4 Jets) ",'scale':None,'reduce':"True",'file_name':'JetCat_gamma_to_gamma','spread':'False' } 
      test_4 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True", 'plot_title':"#mu + jets (2,3 Jets) #rightarrow #mu + jets (Gr4 Jets) (0 b-tag)",'scale':None,'reduce':"False",'file_name':'JetCat_muon_to_muon_zero_btag','spread':'False' } 
      test_5 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#mu#mu + jets (2,3 Jets) #rightarrow #mu#mu + jets (Gr4 Jets) (0 b-tag)",'scale':None,'reduce':"False",'file_name':'JetCat_dimuon_to_dimuon_zero_btag','spread':'False' }
      test_6 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#gamma + jets (2,3 Jets) #rightarrow #gamma + jets (Gr4 Jets) (0 b-tag) ",'scale':None,'reduce':"True",'file_name':'JetCat_gamma_to_gamma_zero_btag','spread':'False' } 
      test_7 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True", 'plot_title':"#mu + jets (2,3 Jets) #rightarrow #mu + jets (Gr4 Jets) (1 b-tag)",'scale':None,'reduce':"False",'file_name':'JetCat_muon_to_muon_gr_one_btag','spread':'False' } 
      test_8 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#mu#mu + jets (2,3 Jets) #rightarrow #mu#mu + jets (Gr4 Jets) (1 b-tag)",'scale':None,'reduce':"False",'file_name':'JetCat_dimuon_to_dimuon_gr_one_btag','spread':'False' }
      test_9 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#gamma + jets (2,3 Jets) #rightarrow #gamma + jets (Gr4 Jets) (1 b-tag) ",'scale':None,'reduce':"True",'file_name':'JetCat_gamma_to_gamma_gr_one_btag','spread':'False' } 

      test_dicts = [test_1,test_2,test_3 ]


    elif self.Classic == "True" :
      print "In classic mode"
      test_1 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True", 'plot_title':"#mu + jets #rightarrow #mu#mu + jets",'scale':None,'reduce':"False",'file_name':'Classic_mu_to_dimuon','spread':'False' } 
      test_2 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "True", 'plot_title':"#gamma + jets #rightarrow #mu#mu + jets ",'scale':None,'reduce':"True",'file_name':'Classic_gamma_to_dimuon','spread':'False' } 
      test_3 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -3.,'box' : "True", 'plot_title':"#gamma + jets #rightarrow #mu + jets",'scale':None,'reduce':"True",'file_name':'Classic_gamma_to_muon','spread':'False' }

      test_dicts = [test_1,test_2,test_3]

    else:
      
      #mumu to mumu
      test_4 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -3.,'box' : "False",'plot_title':"#mu#mu + jets (#alpha_{T} < 0.55) #rightarrow #mu#mu + jets (#alpha_{T}>0.55)",'scale':None , 'reduce':"False",'file_name':'Btag_dimuon_to_dimuon_with_without_alphaT','spread':"False"}
      test_7 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -7.,'box' : "False",'plot_title':"#mu#mu + jets (0-b-tag) #rightarrow #mu#mu + jets (2-b-tag) (no #alpha_{T})",'scale':None , 'reduce':"False",'file_name':'Btag_dimuon_zero_to_dimuon_two_no_alphaT_Cut','spread':"False"}
      test_14 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -14.,'box' : "False",'plot_title':"#mu#mu + jets (0-b-tag) #rightarrow #mu#mu + jets (1-b-tag) (no #alpha_{T})",'scale': None , 'reduce':"False",'file_name':'Btag_mumu_zero_mmuu_one_no_alphaT_Cut','spread':"False" }

      #gamma to mumu
      test_20 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -19.,'box' : "True", 'plot_title':"#gamma + jets (0-b-tag) #rightarrow #mu#mu + jets (0-b-tag) ",'scale':None,'reduce':"True",'file_name':'Btag_gamma_zero_to_dimuon_zero_no_alphaT_Cut','spread':'True' } 
      test_20_b = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -19.,'box' : "True", 'plot_title':"#gamma + jets (>=1-b-tag) #rightarrow #mu#mu + jets (>=1-b-tag) ",'scale':None,'reduce':"True",'file_name':'Btag_gamma_greater_zero_to_dimuon_greater_zero_no_alphaT_Cut','spread':'True' } 
      test_21 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -21.,'box' : "True", 'plot_title':"#gamma + jets #rightarrow #mu#mu + jets ",'scale':None,'reduce':"True",'file_name':'Btag_gamma_to_dimuon_no_alphaT_Cut','spread':'True' }  
      test_21_1 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -19.,'box' : "True", 'plot_title':"#gamma + jets (0-b-tag) #rightarrow #mu#mu + jets (1-b-tag) ",'scale':None,'reduce':"True",'file_name':'Btag_gamma_zero_to_dimuon_one_no_alphaT_Cut','spread':'True' }
      test_21_2 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -19.,'box' : "True", 'plot_title':"#gamma + jets (0-b-tag) #rightarrow #mu#mu + jets (2-b-tag) ",'scale':None,'reduce':"True",'file_name':'Btag_gamma_zero_to_dimuon_two_no_alphaT_Cut','spread':'True' }

      #mu to mumu
      test_2 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True",'plot_title':"#mu + jets (no #alpha_{T}) #rightarrow #mu#mu + jets (no #alpha_{T})" ,'scale':None , 'reduce':"False", 'file_name':'Btag_mu_to_dimuon_no_alphaT_Cut','spread':"False" } 
      test_22 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -22.,'box' : "True", 'plot_title':"#mu + jets (>=1-btag) #rightarrow #mu#mu + jets (0-btag)(no #alphaT) ",'scale':None,'reduce':"False",'file_name':'Btag_greater_zero_mu_to_dimuon_zero_no_alphaT_Cut','spread':'True' }
      test_23 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -23.,'box' : "True", 'plot_title':"#mu + jets (>=1-btag) #rightarrow #mu#mu + jets (>=1-btag)(no #alphaT) ",'scale':None,'reduce':"False",'file_name':'Btag_greater_zero_mu_to_dimuon_greater_zero_no_alphaT_Cut','spread':'True' }
      test_24 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -1.,'box' : "True",'plot_title':"#mu + jets (0-btag) #rightarrow #mu#mu + jets (0-btag) (no #alpha_{T})" ,'scale':None , 'reduce':"False", 'file_name':'Btag_mu_zero_to_dimuon_zero_no_alphaT_Cut','spread':"False" } 
      test_25 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -23.,'box' : "True", 'plot_title':"#mu + jets (>=1-btag) #rightarrow #mu#mu + jets (>=2-btag)(no #alphaT) ",'scale':None,'reduce':"False",'file_name':'Btag_greater_zero_mu_to_dimuon_greater_one_no_alphaT_Cut','spread':'True' }
      test_26 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -23.,'box' : "True", 'plot_title':"#mu + jets (>=2-btag) #rightarrow #mu#mu + jets (>=2-btag)(no #alphaT) ",'scale':None,'reduce':"False",'file_name':'Btag_greater_greater_one_mu_to_dimuon_greater_one_no_alphaT_Cut','spread':'True' }
      
      #mu to mu
      test_3 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "False",'plot_title':"#mu + jets (#alpha_{T} < 0.55) #rightarrow #mu + jets (#alpha_{T}>0.55)",'scale':None , 'reduce':"False", 'file_name':'Btag_mu_to_mu_with_without_alphaT','spread':"False" }
      test_5 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -4.,'box' : "False",'plot_title':"#mu + jets (0-b-tag) #rightarrow #mu + jets (1-b-tag) (no #alpha_{T})",'scale': None , 'reduce':"False",'file_name':'Btag_mu_zero_mu_one_no_alphaT_Cut','spread':"False" } 
      test_6 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",'plot_title':"#mu + jets (0-b-tag) #rightarrow #mu + jets (>1-b-tag) (no #alpha_{T})",'scale':None , 'reduce':"False",'file_name':'Btag_mu_zero_mu_greater_one_no_alphaT_Cut','spread':"False"   }
      test_12 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -11.,'box' : "False",'plot_title':"#mu + jets (1-b-tag) #rightarrow #mu + jets (2-b-tag) (no #alpha_{T})",'scale': None , 'reduce':"False",'file_name':'Btag_mu_one_mu_two_no_alphaT_Cut','spread':"False"   }

      #gamma to mu
      test_49 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -19.,'box' : "True",
                  'plot_title':"#gamma + jets (0-b-tag) #rightarrow #mu + jets (0-b-tag) ",'scale':None,
                  'reduce':"True",'file_name':'Btag_gamma_zero_to_muon_zero_no_alphaT_Cut','spread':'True' } 

      test_80 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",'plot_title':"#mu + jets (0-b-tag) #rightarrow #mu + jets (2-b-tag) (no #alpha_{T})",'scale':None , 'reduce':"False",'file_name':'Btag_mu_zero_mu_two_no_alphaT_Cut','spread':"False"   }

      # test_69 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",
      #           'plot_title':"passed SITV (#mu + jets, >=0 b-tag) #rightarrow failed SITV (#mu + jets, >=0 b-tag) (no #alpha_{T})",
      #           'scale':None , 'reduce':"False",'file_name':'SITV_Passed_to_Failed_Btag_inc_no_alphaT_Cut','spread':"False"}
      # test_69 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",
      #           'plot_title':"no SIT(eq0b, le3j) #rightarrow  SIT (ge1b, ge4j) (no #alpha_{T}, #mu+jets)",
      #           'scale':None , 'reduce':"False",'file_name':'SITV_test1_no_alphaT_Cut','spread':"False"}
      # test_69 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",
      #           'plot_title':"no SIT(eq0b, le3j) #rightarrow  no SIT (ge1b, ge4j) (no #alpha_{T}, #mu+jets)",
      #           'scale':None , 'reduce':"False",'file_name':'SITV_test2_no_alphaT_Cut','spread':"False"}
      # test_69 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",
      #           'plot_title':"no SIT(ge1b, ge4j) #rightarrow  SIT (ge1b, ge4j) (no #alpha_{T}, #mu+jets)",
      #           'scale':None , 'reduce':"False",'file_name':'SITV_test4_no_alphaT_Cut','spread':"False"}

      test_69 = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -5.,'box' : "False",
                'plot_title':"no SIT(eq0b, le3j) #rightarrow  SIT (eq0b, le3j) (no #alpha_{T}, #mu+jets)",
                'scale':None , 'reduce':"False",'file_name':'SITV_test5_no_alphaT_Cut','spread':"False"}

      test_dicts = [test_4,test_2,test_24,test_22,test_3,test_5,test_6,test_12,test_80,test_20,test_20_b,test_21,test_23,test_26,test_49, test_21_1, test_21_2]
      # test_dicts = [test_4, test_3]
      # test_dicts = [test_69]

      test_mhtmet_mumu = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -3.,'box' : "False",'plot_title':"#mu#mu + jets (MHT/MET < 1.25) #rightarrow #mu#mu + jets (MHT/MET > 1.25)",'scale':None , 'reduce':"False",'file_name':'Btag_dimuon_to_dimuon_with_without_MHTMET','spread':"False"}
      test_mhtmet_mu = {'MCS' : [], 'MCSE': [],'MCC': [], 'MCCE':[],'DC':[],'DS':[],'option' : -2.,'box' : "False",'plot_title':"#mu + jets (MHT/MET < 1.25) #rightarrow #mu + jets (MHT/MET > 1.25)",'scale':None , 'reduce':"False", 'file_name':'Btag_mu_to_mu_with_without_MHTMET','spread':"False" }

      # test_dicts = [test_mhtmet_mu, test_mhtmet_mumu]

    """
    We loop through all the dictionaries passed to closure tests from Numbercruncher here and if they fit the category we want to produce a closure test for we pass onto Fill_Dictionary. 

   AlphaT = 0.01 means no alphaT cut
   Jetcat 2 = 2,3 Jets - 3 = >= 4 Jets

    """
    for self.file in dict_list:
      
      for self.entry in self.axis_dir:
        if self.JetCat == "True":

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_1,Control = "Muon", Signal = "Muon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_1,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_2,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_2,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_3,Control = "Photon", Signal = "Photon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_3,Control = "Photon", Signal = "Photon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_4,Control = "Muon", Signal = "Muon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_4,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_5,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_5,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_6,Control = "Photon", Signal = "Photon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_6,Control = "Photon", Signal = "Photon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_7,Control = "Muon", Signal = "Muon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_7,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_8,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_8,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "2":
            self.Fill_Dictionary(test_9,Control = "Photon", Signal = "Photon",Not_Do = 'Signal')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['JetCategory'] == "3":
            self.Fill_Dictionary(test_9,Control = "Photon", Signal = "Photon",Not_Do = 'Control')

        elif self.Classic == "True":

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_1,Control = "Muon", Signal = "DiMuon")

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_2,Control = "Photon", Signal = "DiMuon")

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_3,Control = "Photon", Signal = "Muon")

        else:

          # every instance of aT=0.01 is where a zero alphaT cut is asked for
          # if we ran with an aT cut in muon sample, these would need to be changed (global switch)
          
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_2,Control = "Muon", Signal = "DiMuon") 

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' :
            self.Fill_Dictionary(test_3,Control = "Muon", Signal = "Muon",Not_Do = 'Signal',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "Muon") 
          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive' :
            self.Fill_Dictionary(test_3,Control = "Muon", Signal = "Muon",Not_Do = 'Control')         

            # turn off these with global alphaT
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' :
            self.Fill_Dictionary(test_4,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "DiMuon") 
          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive' :
            self.Fill_Dictionary(test_4,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' :
            self.Fill_Dictionary(test_5,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'One_btag' :
            self.Fill_Dictionary(test_5,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' :
            self.Fill_Dictionary(test_6,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_One_btag' :
            self.Fill_Dictionary(test_6,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' :
            self.Fill_Dictionary(test_80,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Two_btags' :
            self.Fill_Dictionary(test_80,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' :
            self.Fill_Dictionary(test_7,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Two_btags' :
            self.Fill_Dictionary(test_7,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'One_btag' :
            self.Fill_Dictionary(test_12,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Two_btags' :
            self.Fill_Dictionary(test_12,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' :
            self.Fill_Dictionary(test_14,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'One_btag' :
            self.Fill_Dictionary(test_14,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')
 
          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_20,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_20,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_20_b,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_20_b,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_21,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_21,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control') 

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_21_1,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'One_btag':
            self.Fill_Dictionary(test_21_1,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Inclusive':
            self.Fill_Dictionary(test_21_2,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Two_btags':
            self.Fill_Dictionary(test_21_2,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')
        
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_22,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_22,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')
          
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_23,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_23,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_24,Control = "Muon", Signal = "DiMuon") 

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag':
            self.Fill_Dictionary(test_25,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_One_btag':
            self.Fill_Dictionary(test_25,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_One_btag':
            self.Fill_Dictionary(test_26,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_One_btag':
            self.Fill_Dictionary(test_26,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

          if self.file[self.entry]['AlphaT'] == '0.55' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_49,Control = "Photon", Signal = "Photon",Not_Do = 'Signal') 
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags':
            self.Fill_Dictionary(test_49,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          # for SITV test
          # if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Passed":
          #   self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
          # if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Failed":
          #   self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

          # if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['SITV'] == "Passed":
          #   self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 

          # test 4
          # if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['SITV'] == "Failed":
          #   self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Control')
          # if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'More_Than_Zero_btag' and self.file[self.entry]['SITV'] == "Passed":
          #   self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Signal')

          # test 5
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['SITV'] == "Failed":
            self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Control')
          if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Zero_btags' and self.file[self.entry]['SITV'] == "Passed":
            self.Fill_Dictionary(test_69,Control = "Muon", Signal = "Muon",Not_Do = 'Signal')

          # MHT_MET test (using SITV flag for MHTMET differences)
          if True:
            if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Failed":
              self.Fill_Dictionary(test_mhtmet_mu,Control = "Muon", Signal = "Muon",Not_Do = 'Signal',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "Muon") # 0.01 - 0.55 needs subtract option
              # self.Fill_Dictionary(test_mhtmet_mu,Control = "Muon", Signal = "Muon",Not_Do = 'Signal') 
            if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Passed":
              self.Fill_Dictionary(test_mhtmet_mu,Control = "Muon", Signal = "Muon",Not_Do = 'Control',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "Muon")
              # self.Fill_Dictionary(test_mhtmet_mu,Control = "Muon", Signal = "Muon",Not_Do = 'Control')

            if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Failed":
              self.Fill_Dictionary(test_mhtmet_mumu,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "DiMuon")
              # self.Fill_Dictionary(test_mhtmet_mumu,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Signal')
            if self.file[self.entry]['AlphaT'] == '0.01' and self.file[self.entry]['Btag'] == 'Inclusive' and self.file[self.entry]['SITV'] == "Passed":
              self.Fill_Dictionary(test_mhtmet_mumu,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control',Subtract = True,AlphaT="0.55",Btag="Inclusive",SampleName = "DiMuon")
              # self.Fill_Dictionary(test_mhtmet_mumu,Control = "DiMuon", Signal = "DiMuon",Not_Do = 'Control')

    for test in test_dicts:
      if self.JetCat == "True":
        # print test
        self.Make_Plots(test['MCS'],test['MCSE'],test['MCC'],test['MCCE'],test['DC'],test['DS'],test['option'],test['box'],test['plot_title'],test['scale'],test['file_name'],reduce = test['reduce'],spread = test['spread'])
        
      elif self.Classic == "True":
        self.Make_Plots(test['MCS'],test['MCSE'],test['MCC'],test['MCCE'],test['DC'],test['DS'],test['option'],test['box'],test['plot_title'],test['scale'],test['file_name'],reduce = test['reduce'],spread = test['spread'])
      
      else:
        # print test
        self.Make_Plots(test['MCS'],test['MCSE'],test['MCC'],test['MCCE'],test['DC'],test['DS'],test['option'],test['box'],test['plot_title'],test['scale'],test['file_name'],reduce = test['reduce'],spread = test['spread'])


  """
  Fills control/'signal' with the yields which are used by Make_Plots to construct measure of spread
  """

  def Fill_Dictionary(self,closure_dictionary,Control = '',Signal = '',Not_Do = '',Subtract = '',AlphaT = '',Btag = '',SampleName = ''):

          subtract_mc = 0
          subtract_error = 0
          subtract_data = 0

          # if combine_bins is true, then will combine every two bins above 375 GeV
          if self.combine_high_bins:
            next_entry_key = None

            # if int(self.entry[0])>2 and self.entry != "1075" and self.entry != "325" and int(self.entry[0])%2 != 0:
            if self.entry in ['375', '575', '775', '975']:
              # get the next ht bin string
              next_entry_key = str(int(self.entry[0])+1)+self.entry[1:]
            elif self.entry in ['200', '275', '325']:
              # leave the low bins untouched
              next_entry_key = 'low_bin'

            if not next_entry_key:
              return closure_dictionary

          if Subtract == True:
            for subfile in self.dict_list:
              if subfile[self.entry]['AlphaT'] == AlphaT and subfile[self.entry]['Btag'] == Btag and subfile[self.entry]['SampleName'] == SampleName:

                if not self.combine_high_bins or next_entry_key == 'low_bin':
                  subtract_mc = subfile[self.entry]['MCYield']
                  subtract_error = subfile[self.entry]['SM_Stat_Error']
                  subtract_data = subfile[self.entry]['Data']
                else:
                  subtract_mc = subfile[self.entry]['MCYield'] + subfile[next_entry_key]['MCYield']
                  subtract_error = sqrt( pow(subfile[self.entry]['SM_Stat_Error'],2) + pow(subfile[next_entry_key]['SM_Stat_Error'],2) )
                  subtract_data = subfile[self.entry]['Data'] + subfile[next_entry_key]['Data']

          if not self.combine_high_bins or next_entry_key == 'low_bin':
            MC_VAL = self.file[self.entry]['MCYield'] - subtract_mc
            MCE_VAL = self.file[self.entry]['SM_Stat_Error'] - subtract_error
            D_VAL = self.file[self.entry]['Data'] - subtract_data
          else:
            MC_VAL = self.file[self.entry]['MCYield'] + self.file[next_entry_key]['MCYield'] -subtract_mc
            MCE_VAL = sqrt( pow(self.file[self.entry]['SM_Stat_Error'],2) + pow(self.file[next_entry_key]['SM_Stat_Error'],2) ) - subtract_error
            D_VAL = self.file[self.entry]['Data'] + self.file[next_entry_key]['Data'] - subtract_data

          if self.file[self.entry]['SampleName'] == Control and Not_Do != 'Control':
            closure_dictionary['MCC'].append(MC_VAL)
            closure_dictionary['MCCE'].append(MCE_VAL)
            closure_dictionary['DC'].append(D_VAL)
          elif self.file[self.entry]['SampleName'] == Signal and Not_Do != 'Signal':
            closure_dictionary['MCS'].append(MC_VAL)
            closure_dictionary['MCSE'].append(MCE_VAL)
            closure_dictionary['DS'].append(D_VAL)

          return closure_dictionary
 
  
  """
  Closure test made here
  """

  def Make_Plots(self,MCS,MCSE,MCC,MCCE,DC,DS,option,box = '',plot_title='',scale='',file_name='',reduce='',spread='',dc_error='',ds_error=''):

    # Reduce == true for Photon closure tests
    if reduce == "True": hist_low = 375
    else:  hist_low = float(self.settings["bins"][0])

    max = 1.0
    min = -1.0
    if reduce == "True": 
      data = r.TGraphAsymmErrors(8)
      start = 3
    else: 
      data = r.TGraphAsymmErrors(11)
      start = 0

    # hack, because photon plots are broken
    if reduce == "True" and self.combine_high_bins:
      start = 0

    j = 0
    for i in range(start,len(MCS)):
        # ht offset to centre point in ht-bin range
        offset = (self.axis[i+j+1]-self.axis[i+j])/2.0

        if self.combine_high_bins and i>2:
          offset = offset * 2.
        
        #Prediction
        try: prediction = ((MCS[i] / MCC[i]) * DC[i])
        except ZeroDivisionError: prediction = 0.0
        try:val = DS[i] / prediction
        except ZeroDivisionError:val = 0.0
        data.SetPoint(i+1,self.axis[i+j]+offset,val-1.0)
        #Make Errors
        if dc_error:
           eh = dc_error[i]
           el = dc_error[i]
        else:
           eh = sqrt(DC[i])
           el = sqrt(DC[i])
           if DC[i] < 10.: self.Poission(DC[i],eh,el)

        #Total Error on prediction
        try:errh = prediction * sqrt( ((MCSE[i] / MCS[i]) * (MCSE[i] / MCS[i])) + ((MCCE[i] / MCC[i]) * (MCCE[i] / MCC[i])) + ((eh / DC[i]) * (eh / DC[i])) )
        except ZeroDivisionError: errh = 0
        try: errl = prediction * sqrt( ((MCSE[i] / MCS[i]) * (MCSE[i] / MCS[i])) + ((MCCE[i] / MCC[i]) * (MCCE[i] / MCC[i])) + ((el / DC[i]) * (el / DC[i])) )
        except ZeroDivisionError : errl = 0
        # Add to the prediction an extra error = to its statistical error
        ehextra = sqrt(prediction)
        elextra = sqrt(prediction)
        
        if prediction < 10.: self.Poission(prediction,ehextra,elextra)

        #Add these bad boys in quadrature
        errh = sqrt((errh*errh) + (ehextra*elextra))
        errl = sqrt((errl*errl) + (ehextra*elextra))

        # make the numerator: Nobs - Npred
        diffobspred = DS[i] - prediction
        try:errh = fabs((diffobspred / prediction) * sqrt(((errh / diffobspred)*(errh / diffobspred)) + ((errh / prediction)*(errh / prediction))))
        except ZeroDivisionError: errh = 0
        try:errl = fabs((diffobspred / prediction) * sqrt(((errl / diffobspred)*(errl / diffobspred)) + ((errl / prediction)*(errl / prediction))))
        except ZeroDivisionError: errl = 0 
        # Now set errors
        data.SetPointEYhigh(i+1,errh)
        data.SetPointEYlow(i+1,errl)

        if self.combine_high_bins and i>2:
          j += 1

        #if val > 2.2 or val < -2.2:
        #  max = fabs(val)*1.1
        #  min = -fabs(val)*1.1
 
    data.SetTitle("")
     
    data.GetXaxis().SetRangeUser(hist_low,float(self.settings["bins"][-1])+100.0)
    data.GetYaxis().SetRangeUser(min,max)
    data.GetXaxis().SetTitle("H_{T} (GeV)")
    data.GetYaxis().SetTitle("(N_{obs} - N_{pred}) / N_{pred}")
    data.GetYaxis().SetTitleOffset(1.1)
    data.SetLineWidth(3)
    data.SetMarkerStyle(20)
    data.SetMarkerSize(1.5)
    data.Draw("AP")

    if box == 'True':
        pass
        #bv = r.TBox(hist_low,-0.2,1075.,0.2)
        #bv.SetFillColor(kGray) 
        #bv.Draw()
        #data.Draw("p")
     
    """
    Straight lin is fitted to closure test here between all HT bins
    """ 
    fit = r.TF1("fit","pol0",hist_low , float(self.settings["bins"][-1])+100.0)
    data.Fit(fit,"R")
    fit.SetLineColor(2)
    fit.Draw("SAME")

      
    tex = r.TLatex(0.12,0.84,"CMS, %s fb^{-1}, #sqrt{s} = 8 TeV" % self.Lumo )
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.Draw("SAME")
    pt = r.TPaveText(0.12,0.90,0.5,0.95,"blNDC")
    pt.SetBorderSize(0)
    pt.SetFillColor(0)
    pt.SetTextSize(0.04)
    pt.AddText(plot_title)
    pt.Draw("SAME")
    self.c1.SaveAs("./ClosureTests/%s%s.png" %(file_name,self.jetmult))
    self.c1.SaveAs("./ClosureTests/%s%s.C" %(file_name,self.jetmult))
    #self.c1.Modified()

  def Poission(self,x,errh,errl):
    poisson_eh = [ 1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00, 3.16 ]
    poisson_el = [ 0.00, 1.00, 2.00, 2.14, 2.30, 2.49, 2.68, 2.86, 3.03, 3.19, 3.16 ]

    if x<10:
    # Apply Poission errors
      n = int(x)
      f = x - float(int(x))
      errh = poisson_eh[n] + f*( poisson_eh[n+1] - poisson_eh[n])
      errl = poisson_el[n] + f*(poisson_eh[n+1] - poisson_el[n])
    return errh,errl
      
          

def dict_printer(dicto = {}, indent = 1):

  # print "> Outputting dictionary format.\n"
  
  print "{ (%d keys)\n" % len(dicto)
  for key in dicto:
    print "\t"*indent, "'%s': " % key,
    if dict == type(dicto[key]):
      dict_printer(dicto[key], indent+1)
    else:
      print dicto[key]
  print "\t"*indent, "}\n"

