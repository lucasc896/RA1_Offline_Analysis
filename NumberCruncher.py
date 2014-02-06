#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime, time, sleep
from optparse import OptionParser
import array, ast
from math import *
from plottingUtils import *
from Closure_Tests import *
from Btag_calculation_v3 import *
from Calculation_Template_v4 import *

"""
This is where Trigger corrections are applied to MC. 
"""

def MC_Scaler(htbin,jetmult,mc_yield,sample = '',error = '',Analysis = '',btagbin = '', alphat_slice = None):

    if Analysis == "8TeV":
        AlphaT_Scale = {"200_2":0.816,  "200_3":0.740,
                        "275_2":0.901,  "275_3":0.666,
                        "325_2":0.988,  "325_3":0.971,
                        "375_2":0.994,  "375_3":0.988,
                        "475_2":0.99,   "475_3":0.99, 
                        "575_2":1.,     "575_3":1.,
                        "675_2":1.,     "675_3":1.,
                        "775_2":1.,     "775_3":1.,
                        "875_2":1.,     "875_3":1.,
                        "975_2":1.,     "975_3":1.,
                        "1075_2":1.,    "1075_3":1.,}
                        
        AlphaT_Error = {"200_2":0.004,  "200_3":0.033,
                        "275_2":0.004,  "275_3":0.013,
                        "325_2":0.002,  "325_3":0.008,
                        "375_2":0.002,  "375_3":0.006,
                        "475_2":0.002,  "475_3":0.005,
                        "575_2":0.002,  "575_3":0.005,
                        "675_2":0.002,  "675_3":0.005,
                        "775_2":0.002,  "775_3":0.005,
                        "875_2":0.002,  "875_3":0.005,
                        "975_2":0.002,  "975_3":0.005,
                        "1075_2":0.002, "1075_3":0.005,}

        DiMuon_Scale = {"150":0.95,
                        "200":0.95,
                        "275":0.96,
                        "325":0.96,
                        "375":0.96,
                        "475":0.96,
                        "575":0.97,
                        "675":0.97,
                        "775":0.98,
                        "875":0.98,
                        "975":0.98,
                        "1075":0.98}
        muon_eff = 0.88

        if float(alphat_slice.split("_")[0]) == 0.6:
          # override some values for running with 0.6 alphaT cut
          print ">>> WARNING: running with aT > 0.6 trigger effs"

          AlphaT_Scale["275_2"] = 0.94
          AlphaT_Scale["275_3"] = 0.74
   
   
    scale_factor = htbin +'_'+ jetmult
    if jetmult == "all" : scale_factor = htbin +'_2'
    if mc_yield == 0: return float(mc_yield)

    if sample == "Muon":
      if error:
        return float((error*muon_eff)*math.sqrt(((mc_yield/error)*(mc_yield/error))+((0.01/muon_eff)*(0.01/muon_eff))))
      else:return float(mc_yield*muon_eff) 
 
    elif sample == "DiMuon":
        if error: return float((error*DiMuon_Scale[htbin])*math.sqrt(((mc_yield/error)*(mc_yield/error))+((0.01/DiMuon_Scale[htbin])*(0.01/DiMuon_Scale[htbin]))))
        else: return float(mc_yield*DiMuon_Scale[htbin])

    elif sample == "Had":
      if error: 
        return float((error*AlphaT_Scale[scale_factor])*math.sqrt(((mc_yield/error)*(mc_yield/error))+((AlphaT_Error[scale_factor]/AlphaT_Scale[scale_factor])*(AlphaT_Error[scale_factor]/AlphaT_Scale[scale_factor]))))
      else:return float(mc_yield*AlphaT_Scale[scale_factor])

    else: return mc_yield


class Number_Extractor(object):

  def __init__(self,sample_settings,sample_list,number,c_file = "",Triggers = "",Closure = "",Stats = "",AlphaT='',Trans_Plots = '',Calculation = '',Split_Lumi = '',Analysis_category = '',Template = '',Combine = '',Do_sys = '',Working_Point = '',Feasibility = "",RunOption = "",Sitv = "False"):

    from time import time
    self.baseTime = time()

    print "\n\nGetting Numbers\n\n"
    self.Systematic = Do_sys
    self.Settings = sample_settings
    self.Analysis = sample_settings["Analysis"]
    self.Keep_AlphaT = AlphaT
    self.Make_Root_Stats_File = Stats
    self.Make_Closure_Tests = Closure
    self.Feasibility = Feasibility
    self.RunOption = RunOption
    self.Trigger_Scaling = Triggers
    self.c_file = c_file
    self.Make_2D_Histos = Trans_Plots
    self.number = number
    self.sitv = Sitv
    self.MHTMETcorrection = sample_settings["MHTMET"]
    print " MHTMET Correction Applied :  %s" %self.MHTMETcorrection
    if self.RunOption == "MCNormalisation": self.CombineBins = "True"
    else : self.CombineBins = "False"
    self.analysis_category = Analysis_category
    self.Lumi_List = {"Had":0,"Muon":0,"DiMuon":0,"Photon":0,"OSOF":0,"OSSF":0,"SSOF":0,"SSSF":0}
    self.btag_names = {"Zero_btags":"eq0","One_btag":"eq1","Two_btags":"eq2","Three_btags":"eq3","More_Than_Zero_btag":"gr0","More_Than_One_btag":"gr1","Inclusive":"Inc","More_Than_Three_btag":"eq4"}
    self.cat_names = {"2":"eq2_and_3","3":"greq4","all":"inclusive"}
  
    self.btagbin = {"Inclusive":1,"Zero_btags":1,"One_btag":2,"Two_btags":3,"Three_btags":4,"More_Than_Three_btag":5}

    print "Analysis conducted for %s" %self.Analysis
    """
    Lumonosities are passed from config file and set here to be applied to MC
    """

    if Split_Lumi == "True":
        print "Multiple Luminosity being used" 
        for key in self.Settings["Multi_Lumi"]:
                print "Sample %s   : Lumi %sfb" %(key , self.Settings["Multi_Lumi"][key])
                self.Lumi_List[key] = self.Settings["Multi_Lumi"][key]
    else: 
        print "Single Luminosity of All Samples is %s fb\n\n" %self.Settings["Lumo"]
        for entry in self.Lumi_List: self.Lumi_List[entry] = self.Settings["Lumo"]
    print self.Lumi_List
    if Template:
      # For Template method not used in RA1 analysis
      Template_Calc(sample_settings,sample_list,Template,float(self.Settings["Lumo"]),self.Systematic,Working_Point)
      return
    if Calculation: 
      # When formula method is used (Standard RA1), samples are passed onto Btag_Calc class in btag_calculation.
      # This fills up self.return_dict, which contains all the btag effs
      # note, this is a call to the "Make_Dict" function of BtagCalc!
      self.return_dict = Btag_Calc(sample_settings,sample_list,Calculation,number,AlphaT,self.Lumi_List,self.Analysis,self.analysis_category).Make_Dict(sample_settings,sample_list,number) 
      self.Form_Vanilla = "Formula"
    else:
      # Uncorrected yields are produced here. Used as sanity check as formula method == uncorreced yields for inclusive btag multiplicity or else something has gone wrong
      self.Form_Vanilla = "Vanilla"
      self.Create_Dictionary(sample_settings,sample_list)
    self.Prediction_Maker(sample_settings,self.return_dict)

  def Create_Dictionary(self,settings,samples):

         """
         This is where dictionary is created for Uncorrected yields. 
         We loop through all samples and all HT bins and pull out the integral of the number of btags histogram to determine the yields and error.
         Same process is done in Btag_Calc but the yields are calculated through a formula rather than just pull the number from a histogram
         """
         print "In uncorrected yields"
         # print "number:", self.number
         # print self.btagbin[self.number]
         table_entries = "{" 
         for key,fi in sorted(samples.iteritems()):
           i = 0
           for dir in settings['dirs']:
              fixed_dir = dir
              for alphat in settings['AlphaTSlices']:
                dir = fixed_dir
                lower = float(alphat.split('_')[0])
                higher = float(alphat.split('_')[1])
                table_entries += "\t\"%s_%d\"  : "%(key,i)
                i+=1
                table_entries += "{\"HT\":\"%s\","%(dir.split('_')[0])
                for histName in settings['plots']:
                    histName = str(histName+self.analysis_category)
                    # print histName
                    checkht = dir
                    dir = fi[1]+dir
                    Luminosity = self.Lumi_List[fi[3]]
                    normal =  GetSumHist(File = ["%s.root"%fi[0]], Directories = [dir], Hist = histName, Col = r.kBlack, Norm = None if "n" == key[0] else [float(Luminosity*1000)/100.], LegendText = "nBtag")  
                    normal.HideOverFlow()
                    err = r.Double(0.0)
                    # normal.hObj.IntegralAndError(self.btagbin[self.number],normal.hObj.GetNbinsX(),err)
                    lo_bin = normal.hObj.FindBin(lower)
                    val = normal.hObj.IntegralAndError(lo_bin,normal.hObj.GetNbinsX(),err)
                    # table_entries +=" \"Yield\": %.3e ,\"Error\":\"%s\",\"SampleType\":\"%s\",\"Category\":\"%s\",\"AlphaT\":%s},\n"%((normal.hObj.GetBinContent(self.btagbin[self.number]) if self.number not in ["More_Than_Three_btag","Inclusive"] else normal.hObj.Integral(self.btagbin[self.number],normal.hObj.GetNbinsX())),(normal.hObj.GetBinError(self.btagbin[self.number]) if self.number not in ["More_Than_Three_btag","Inclusive"]  else err),fi[2],fi[3],lower)
                    # table_entries +=" \"Yield\": %.3e ,\"Error\":\"%s\",\"SampleType\":\"%s\",\"Category\":\"%s\",\"AlphaT\":%s},\n"%((normal.hObj.Integral(lo_bin,normal.hObj.GetNbinsX()) if str(checkht[0:3]) in ["275","325"] else (normal.hObj.Integral())),err,fi[2],fi[3],lower)
                    table_entries +=" \"Yield\": %.3e ,\"Error\":\"%s\",\"SampleType\":\"%s\",\"Category\":\"%s\",\"AlphaT\":%s},\n"%(normal.hObj.Integral(lo_bin,normal.hObj.GetNbinsX()),err,fi[2],fi[3],lower)
                    normal.a.Close()
         
         table_entries +="}"
         # Do a literal eval to turn this string into a dictionary
         self.return_dict = ast.literal_eval(table_entries)
         return self.return_dict




  def Prediction_Maker(self,settings,dict):

      """
      This is where the the initial dictionary we created above is sorted into individual processes and selections to make it easier to put into tables and sort for closure tests. 
      """
 
      if self.CombineBins == "True":
        self.bins = tuple(settings["bins"]+["200_upwards"])
      else:
        self.bins = tuple(settings["bins"])

      entries = ('Data','MCYield','Tot_Error','SM_Stat_Error','TTbar','WJets','Zinv','DY','DiBoson','SingleTop','Photon','Btag','SampleName','JetCategory','AlphaT','SITV')
      yields = ('Yield','Error')

      self.process = ["TTbar","WJets","Zinv","DY","DiBoson","SingleTop","Photon"]      
      analysis_type = "%s" %("Feasibility" if self.Feasibility == "True" else "RA1")

      if self.Make_Closure_Tests != "True" and self.Make_Root_Stats_File != "True": 
        self.table = open('./%s/%s_%s_Predictions_btags_%s_category_%s.tex' % ("TexFiles" if self.RunOption != "MCNormalisation" else "NormalisationTables" ,analysis_type,self.Form_Vanilla,self.btag_names[self.number],self.cat_names[self.analysis_category])  ,'w')
        self.Make_Preamble()

      for slices in settings['AlphaTSlices']:
       
        self.current_slice = str(slices).split('_')[0]
        self.Had_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.Had_Zinv_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.Had_Muon_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.Muon_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.DiLepton_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.Photon_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.DiMuon_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.SSOF_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.SSSF_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.OSOF_Yield_Per_Bin = dict.fromkeys(self.bins)
        self.OSSF_Yield_Per_Bin = dict.fromkeys(self.bins)


        """
        Create these empty dictionaries to be filled.
        eg. Had_Yield_Per_Bin. Will include all SM processes + Data yields in the format
        { "Data":0  , "SampleName":"Had",JetCategory:"all",AlphaT:0.55,TTbar:{Yield:0,Error:0}..... etc
        """

        dictionaries = [ self.Had_Yield_Per_Bin, self.Had_Muon_Yield_Per_Bin,self.Had_Zinv_Yield_Per_Bin,self.Muon_Yield_Per_Bin, self.Photon_Yield_Per_Bin, self.DiMuon_Yield_Per_Bin,self.DiLepton_Yield_Per_Bin, self.SSOF_Yield_Per_Bin,self.SSSF_Yield_Per_Bin, self.OSOF_Yield_Per_Bin, self.OSSF_Yield_Per_Bin]

        # List of Dictionaries for Jad's Closure Tests
        jad_dictionaries = [self.Muon_Yield_Per_Bin,self.DiMuon_Yield_Per_Bin,self.Photon_Yield_Per_Bin]

        for dicto in dictionaries:
          for key in self.bins:
            dicto[key] = dict.fromkeys(entries)
            dicto[key]['Data'] = 0
            dicto[key]['MCYield'] = 0
            dicto[key]['AlphaT'] = self.current_slice
            dicto[key]['SM_Stat_Error'] = 0
            dicto[key]['Tot_Error'] = []
            dicto[key]['Btag'] = self.number
            dicto[key]['JetCategory'] = self.analysis_category
            dicto[key]['SITV'] = self.sitv
            for SM in self.process:
                dicto[key][SM] = dict.fromkeys(yields,0) 
                dicto[key][SM]['Process_Error'] = []

        # Take mean point of each HT bin for MHT_MET sideband correction
        # meanbin_dict = {"150":178.2,"200":235.2,"275":297.5,"325":347.5,"375":416.4,"475":517.3,"575":618.4,"675":716.9,"775":819.9,"875":919.,"975":1019.,"1075":1289.}

        # correction_factors = {'775': {'WJets': {'Correction': 0.64340559024949506, 'Error': 0.025173711670053014}, 'TTbar': {'Correction': 0.69374291672306865, 'Error': 0.061739168909783371}, 'DY': {'Correction': 0.66593575915723469, 'Error': 0.076039960431377771}}, '150': {'WJets': {'Correction': 0.90380868649372859, 'Error': 0.010229557535701412}, 'TTbar': {'Correction': 1.0680665793720683, 'Error': 0.033513977482678474}, 'DY': {'Correction': 0.90525005563513883, 'Error': 0.029135953140267436}}, '975': {'WJets': {'Correction': 0.56261042668049566, 'Error': 0.034663112814916713}, 'TTbar': {'Correction': 0.57760166499575716, 'Error': 0.088117650729789235}, 'DY': {'Correction': 0.59168380897997008, 'Error': 0.10490484043777346}}, '875': {'WJets': {'Correction': 0.60319061933192675, 'Error': 0.029873803940809993}, 'TTbar': {'Correction': 0.63593478992157915, 'Error': 0.07479745299254123}, 'DY': {'Correction': 0.62897760615589404, 'Error': 0.090350238066029293}}, '200': {'WJets': {'Correction': 0.88067797668241277, 'Error': 0.0084424927326850474}, 'TTbar': {'Correction': 1.0348166981643498, 'Error': 0.027222811671515277}, 'DY': {'Correction': 0.88399259124486207, 'Error': 0.02349473008298689}}, '675': {'WJets': {'Correction': 0.68520318868046903, 'Error': 0.02037154389218699}, 'TTbar': {'Correction': 0.75382603539666526, 'Error': 0.048440120147728173}, 'DY': {'Correction': 0.70434837024843633, 'Error': 0.061371127488360877}}, '475': {'WJets': {'Correction': 0.76620125321272559, 'Error': 0.01169608637548657}, 'TTbar': {'Correction': 0.87025895274860599, 'Error': 0.025143611356439763}, 'DY': {'Correction': 0.77878678941158064, 'Error': 0.034533050042142639}}, '575': {'WJets': {'Correction': 0.72517467844212868, 'Error': 0.015927912986835845}, 'TTbar': {'Correction': 0.81128416344859999, 'Error': 0.036262350826656561}, 'DY': {'Correction': 0.7410827604667215, 'Error': 0.047713629793532934}}, '1075': {'WJets': {'Correction': 0.45304390652163162, 'Error': 0.04771746510506801}, 'TTbar': {'Correction': 0.42010222769603778, 'Error': 0.12443907413254611}, 'DY': {'Correction': 0.49099055660497531, 'Error': 0.14450431041652143}}, '275': {'WJets': {'Correction': 0.85539651666057126, 'Error': 0.0072613111742462081}, 'TTbar': {'Correction': 0.99847516133556269, 'Error': 0.021492256158750427}, 'DY': {'Correction': 0.86075855560426151, 'Error': 0.019784516261131695}}, '325': {'WJets': {'Correction': 0.83510642033485571, 'Error': 0.0071679324751279362}, 'TTbar': {'Correction': 0.96930859887265175, 'Error': 0.018506199594173101}, 'DY': {'Correction': 0.84211165701629953, 'Error': 0.019657109235429113}}, '375': {'WJets': {'Correction': 0.80714666759801967, 'Error': 0.0083232502183881781}, 'TTbar': {'Correction': 0.92911707579876035, 'Error': 0.018180212731800389}, 'DY': {'Correction': 0.81641623076208791, 'Error': 0.023667891499540902}}}

        

        # Loop through dictionary created from CreateDictionary or Btag_Calc.MakeDict() 
        for entry,fi in dict.iteritems():
          
          """
          Apply derived MHT_MET sidebands here for each of the different samples
          """ 

          # changed this to float comparison, so stop reliance on matching trailing zero's in strings
          if float(fi['AlphaT']) == float(slices.split('_')[0]) :
           
            # midht = meanbin_dict[dict[entry]["HT"]]
            
            if self.MHTMETcorrection == "True": 
             
              # I think the next 7 lines are now redundant...
              err_stat = 0.0
              err_fit = 0.0
             
              try: err_stat = pow(float(dict[entry]["Error"])/dict[entry]["Yield"] ,2)
              except ZeroDivisionError : pass

              try: err_stat = pow(float(dict[entry]["Error"])/dict[entry]["Yield"] ,2)
              except ZeroDivisionError : pass
 
              scale_factor = 1.

              if dict[entry]["SampleType"] in ["Photon"]:
                scale_factor = settings["sb_corrs"]["Photon"]
              if dict[entry]["SampleType"] in ["DY"]:
                scale_factor = settings["sb_corrs"]["DY"]
              if dict[entry]["SampleType"] in ["Zinv"]:
                scale_factor = settings["sb_corrs"]["Zinv"]
              if dict[entry]["SampleType"] in ["WJets"]:
                scale_factor = settings["sb_corrs"]["WJets"]
              if dict[entry]["SampleType"] in ["TTbar","SingleTop"]:
                scale_factor = settings["sb_corrs"]["Top"]

              # apply weight factor
              dict[entry]["Error"] = float(dict[entry]["Error"]) * scale_factor
              dict[entry]["Yield"] = float(dict[entry]["Yield"]) * scale_factor


            Error = float(dict[entry]["Error"]) 
            if dict[entry]["SampleType"] == "Data":
              if dict[entry]["Category"] == "Had": 
                   self.Had_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                   self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                   self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                   self.Had_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "Had"
                   self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "Had"
                   self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "Had"

              if dict[entry]["Category"] == "Muon":
                    self.Muon_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                    self.Muon_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "Muon" 
              if dict[entry]["Category"] == "DiMuon":
                    self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                    self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "DiMuon" 
              if dict[entry]["Category"] == "Photon":
                    self.Photon_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
                    self.Photon_Yield_Per_Bin[dict[entry]["HT"]]["SampleName"] = "Photon" 
              if dict[entry]["Category"] == "DiLepton": self.DiLepton_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
              if dict[entry]["Category"] == "SSOF": self.SSOF_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
              if dict[entry]["Category"] == "SSSF": self.SSSF_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
              if dict[entry]["Category"] == "OSSF": self.OSSF_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]
              if dict[entry]["Category"] == "OSOF": self.OSOF_Yield_Per_Bin[dict[entry]["HT"]]["Data"] = dict[entry]["Yield"]

            elif dict[entry]["Category"] == "Had" :
               
                  self.Had_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.Had_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]]["Error"] = Error
                  self.Had_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.Had_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]
        
                  if dict[entry]["SampleType"] == "Zinv": 

                    self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                    self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                    self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                    self.Had_Zinv_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

                  else: 

                    self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                    self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                    self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                    self.Had_Muon_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "Muon":

                  self.Muon_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"]=  dict[entry]["Yield"]
                  self.Muon_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.Muon_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.Muon_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "DiLepton":

                  self.DiLepton_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.DiLepton_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.DiLepton_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.DiLepton_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "DiMuon":

                  self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"]=  dict[entry]["Yield"]
                  self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.DiMuon_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "Photon":

                  self.Photon_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.Photon_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.Photon_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.Photon_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "SSOF":

                  self.SSOF_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.SSOF_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.SSOF_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.SSOF_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "SSOF":

                  self.SSSF_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.SSSF_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.SSSF_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.SSSF_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "OSOF":

                  self.OSOF_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.OSOF_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"]    ]["Error"] = Error
                  self.OSOF_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.OSOF_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]

            elif dict[entry]["Category"] == "OSSF":

                  self.OSSF_Yield_Per_Bin[dict[entry]["HT"]][dict[entry]["SampleType"]]["Yield"] =  dict[entry]["Yield"]
                  self.OSSF_Yield_Per_Bin[dict[entry]["HT"]][ dict[entry]["SampleType"] ]["Error"] = Error
                  self.OSSF_Yield_Per_Bin[dict[entry]["HT"]]["Tot_Error"].append(Error)
                  self.OSSF_Yield_Per_Bin[dict[entry]["HT"]]["MCYield"] += dict[entry]["Yield"]


        """
        Calculate total MC error by adding in quadrature the errors from each of the individual SM processed
        """
        for bin in self.Muon_Yield_Per_Bin: 
          for sample in dictionaries: 
            try:  sample[bin]["SM_Stat_Error"] = math.sqrt(reduce(lambda x,y : x+y,map(lambda x: x*x, sample[bin]["Tot_Error"])))
            except TypeError: pass


        """
        Apply Trigger corrections here
        """
        if self.Trigger_Scaling == "True":
          print "Apply MC Correction For Scaling"
          for bin in self.Muon_Yield_Per_Bin:
            for sample in dictionaries:

              sample[bin]["MCYield"] = MC_Scaler(bin,self.analysis_category,sample[bin]["MCYield"],sample = sample[bin]["SampleName"],Analysis = self.Analysis,btagbin = self.number, alphat_slice = slices )
              sample[bin]["SM_Stat_Error"] = MC_Scaler(bin,self.analysis_category,sample[bin]["SM_Stat_Error"],sample = sample[bin]["SampleName"],error = sample[bin]["MCYield"],Analysis = self.Analysis, btagbin = self.number, alphat_slice = slices )
               
              for SM in self.process:
               
                sample[bin][SM]["Yield"] = MC_Scaler(bin,self.analysis_category, sample[bin][SM]["Yield"],sample = sample[bin]["SampleName"],Analysis = self.Analysis,btagbin = self.number, alphat_slice = slices )
                sample[bin][SM]["Error"] = MC_Scaler(bin,self.analysis_category,sample[bin][SM]["Error"],sample = sample[bin]["SampleName"],error = sample[bin][SM]["Yield"],Analysis = self.Analysis, btagbin = self.number, alphat_slice = slices )


        """
        This is where we sum up the total yields across all HT bins. Still deciding wether to use as an overall residual correction. 
        Can just be used to determine overall Data/MC ratio.
        Turn combine bins off if you don't want to include it 
        """
        
        if self.CombineBins == "True":
            for sample in dictionaries:
                for bin in settings["bins"] :
                      sample["200_upwards"]["Data"] += sample[bin]["Data"] 
                      sample["200_upwards"]["MCYield"] += sample[bin]["MCYield"]
                      for SM in self.process:
                         sample["200_upwards"][SM]["Yield"] += sample[bin][SM]["Yield"] 
                         sample["200_upwards"][SM]["Process_Error"].append(sample[bin][SM]["Error"])
                for SM in self.process:
                    try:  sample["200_upwards"]["Tot_Error"].append(math.sqrt(reduce(lambda x,y : x+y,map(lambda x: x*x, sample["200_upwards"][SM]["Process_Error"]))))
                    except TypeError: pass
                try:  sample["200_upwards"]["SM_Stat_Error"] = math.sqrt(reduce(lambda x,y : x+y,map(lambda x: x*x, sample["200_upwards"]["Tot_Error"])))
                except TypeError: pass


        
        
        """
        Now we make all the tex tables from all the smaller dictionaries we have created
        """
        if self.Make_Closure_Tests == "True" or self.Make_Root_Stats_File == "True":pass
        
        else:

          if self.Feasibility == "True":
            self.Produce_Tables(self.Had_Yield_Per_Bin,category = "Had_Tables")
            self.Produce_Tables(self.Muon_Yield_Per_Bin,category = "Muon_Tables")
            self.Produce_Tables(self.OSOF_Yield_Per_Bin,category = "OSOF_Tables")
            self.Produce_Tables(self.OSSF_Yield_Per_Bin,category = "OSSF_Tables")
            self.Produce_Tables(self.SSOF_Yield_Per_Bin,category = "SSOF_Tables")
            self.Produce_Tables(self.SSSF_Yield_Per_Bin,category = "SSSF_Tables")

          else:   

            if self.RunOption == "MCNormalisation":  

              self.MC_Ratio(self.Muon_Yield_Per_Bin,"WJets","TTbar")
              self.Produce_Tables(self.Dict_For_Table,category = "Muon_Tables")
              self.MC_Ratio(self.DiMuon_Yield_Per_Bin,"DY")
              self.Produce_Tables(self.Dict_For_Table,category = "DiMuon_Tables")
              self.MC_Ratio(self.Photon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_Tables")


            else:
   
              self.Table_Prep(self.Muon_Yield_Per_Bin,self.Had_Muon_Yield_Per_Bin, comb = self.DiMuon_Yield_Per_Bin, comb_test=self.Had_Zinv_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Combined_SM", dict2 = self.Combination_Pred_Table)

              self.Table_Prep(self.Muon_Yield_Per_Bin,self.Had_Muon_Yield_Per_Bin, comb = self.Photon_Yield_Per_Bin, comb_test=self.Had_Zinv_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Combined_SM_Photon", dict2 = self.Combination_Pred_Table)
            
              self.Table_Prep(self.Muon_Yield_Per_Bin,self.Had_Yield_Per_Bin,make_hist = "Total_SM")
              self.Produce_Tables(self.Dict_For_Table,category = "Total_SM")
            
              self.Table_Prep(self.Muon_Yield_Per_Bin,self.Had_Muon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Muon_WJet_TTbar")
            
              self.Table_Prep(self.Photon_Yield_Per_Bin,self.Had_Zinv_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_Zinv")
            
              self.Table_Prep(self.DiMuon_Yield_Per_Bin,self.Had_Zinv_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Di_Muon_Zinv")
            
              self.Table_Prep(self.Muon_Yield_Per_Bin,self.DiMuon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Di_Muon")
           
              self.Table_Prep(self.Photon_Yield_Per_Bin,self.DiMuon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_DiMuon")

              self.Table_Prep(self.Photon_Yield_Per_Bin,self.Muon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_Muon")

              self.Produce_Tables(self.Had_Yield_Per_Bin,category = "Had_Tables")


              self.MC_Ratio(self.Photon_Yield_Per_Bin)
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_Tables")
              self.MC_Ratio(self.Muon_Yield_Per_Bin,"WJets","TTbar")
              self.Produce_Tables(self.Dict_For_Table,category = "Muon_Tables")
              self.MC_Ratio(self.DiMuon_Yield_Per_Bin,"DY")
              self.Produce_Tables(self.Dict_For_Table,category = "DiMuon_Tables")


            
        # Additional Functions Jads Closure Tests, Stat File Root Maker
        if self.Make_Closure_Tests != "True" and self.Make_Root_Stats_File != "True":self.Make_End()

        #Make Output Root File
        # This outputs all the dictionaries to root files if this option is specified. Trigger corrections are not applied here. Ted does them himself.
        if self.Make_Root_Stats_File == "True":
          self.Begin_Stats_Root_Output(self.Settings,analysis = analysis_type)
          self.Format_Stats_Root_Output(dictionaries,settings, analysis = analysis_type)

        # This outputs the dictionaries used in Closure tests to an output file if the closure test option is specified
        if self.Make_Closure_Tests == "True" :self.Jad_Output(jad_dictionaries)    

  def Jad_Output(self,input):
    for file in input: 
        self.c_file.append(file)


  """
  This is used in the MHT/MET sideband method. A pure MC ratio is produced of WJets,TTbar etc with other processes subtracted away.
  
  eg. Data/MC(WJets) =  (Data - (TTbar,singletop,DY...) ) / WJets 

  This is used to check purity of process in a certain b-tag,jet mutiplicity and also we take these ratios and put it into the MHT/MET fit

  """ 

  def MC_Ratio(self,dicto,*pureprocess):

      eh =  [1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00 ]
      el =  [0.00, 1.00, 2.00, 2.14, 2.30, 2.49, 2.68, 2.86, 3.03, 3.19 ]

      self.Dict_For_Table = dict.fromkeys(self.bins)
      entries = ('MCRatio','RatioError')
      dictionaries = [self.Dict_For_Table]
 
 
      for key in self.bins: 

             self.Dict_For_Table[key] = dict.fromkeys(entries,0)
             for entry in pureprocess: self.Dict_For_Table[key][entry+"Ratio"] = 0 

      for bin in sorted(dicto.iterkeys()):

         try:self.Dict_For_Table[bin]['MCRatio'] = dicto[bin]["Data"]/dicto[bin]["MCYield"]
         except ZeroDivisionError: pass

         for i in pureprocess :
            data_yield = dicto[bin]["Data"] 
            mc_yield = dicto[bin]["MCYield"]

            for process in self.process: 
                if process != i: 
                     data_yield = data_yield - dicto[bin][process]["Yield"]
                     mc_yield = mc_yield - dicto[bin][process]["Yield"] 
            try:self.Dict_For_Table[bin][i+"Ratio"] = data_yield/mc_yield
            except ZeroDivisionError: self.Dict_For_Table[bin][i+"Ratio"] = 0    

         try: mc_error =  dicto[bin]["SM_Stat_Error"]/dicto[bin]["MCYield"] 
         except ZeroDivisionError: mc_error = 0
         try :data_error =  (sqrt(dicto[bin]["Data"]) if dicto[bin]["Data"] > 9 else float(eh[int(dicto[bin]["Data"])])) /dicto[bin]["Data"] 
         except ZeroDivisionError: data_error = 0
        
         self.Dict_For_Table[bin]['RatioError'] = self.Dict_For_Table[bin]['MCRatio'] * sqrt( pow(mc_error,2) + pow(data_error,2) )  


  """
  This function produced Translation factors between selections and also the Data prediction and its error
  """

  def Table_Prep(self,control,test,comb="",comb_test="",category="",make_hist=""):

      eh =  [1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00 ]
      el =  [0.00, 1.00, 2.00, 2.14, 2.30, 2.49, 2.68, 2.86, 3.03, 3.19 ]
      trans_num = []
      trans_error = []
      self.Dict_For_Table = dict.fromkeys(self.bins)
      self.Combination_Pred_Table = dict.fromkeys(self.bins)
      entries = ('Data_Pred','Prediction','Pred_Error','Data','Data_Error','Trans','Trans_Error')
      dictionaries = [self.Dict_For_Table,self.Combination_Pred_Table]

      for dicto in dictionaries:
        for key in self.bins: dicto[key] = dict.fromkeys(entries,0)

      #for bin in control: 
      for bin in  sorted(control.iterkeys()):
          try:
            self.Dict_For_Table[bin]['Trans'] = test[bin]["MCYield"]/control[bin]["MCYield"]
          except ZeroDivisionError: pass
          try: control_error =  control[bin]["SM_Stat_Error"]/control[bin]["MCYield"] 
          except ZeroDivisionError: control_error = 0
          try :test_error =  test[bin]["SM_Stat_Error"]/test[bin]["MCYield"] 
          except ZeroDivisionError: test_error = 0
          self.Dict_For_Table[bin]['Trans_Error'] = self.Dict_For_Table[bin]['Trans'] * math.sqrt((control_error*control_error)+(test_error*test_error))
          self.Dict_For_Table[bin]['Data_Pred'] = control[bin]["Data"]
          self.Dict_For_Table[bin]['Data_Error'] = sqrt(control[bin]["Data"]) if control[bin]["Data"] > 9 else float(eh[int(control[bin]["Data"])])
          self.Dict_For_Table[bin]['Prediction'] = control[bin]["Data"]*self.Dict_For_Table[bin]['Trans']
          self.Dict_For_Table[bin]['Data'] = test[bin]["Data"]
          try:self.Dict_For_Table[bin]['Pred_Error'] = self.Dict_For_Table[bin]['Prediction']*math.sqrt(((self.Dict_For_Table[bin]['Data_Error']/self.Dict_For_Table[bin]['Data_Pred'])*(self.Dict_For_Table[bin]['Data_Error']/self.Dict_For_Table[bin]['Data_Pred'])) +((self.Dict_For_Table[bin]['Trans_Error']/self.Dict_For_Table[bin]['Trans'])*(self.Dict_For_Table[bin]['Trans_Error']/self.Dict_For_Table[bin]['Trans'])))
          except ZeroDivisionError: self.Dict_For_Table[bin]['Pred_Error'] = 0
          trans_num.append(self.Dict_For_Table[bin]['Trans'])
          trans_error.append( self.Dict_For_Table[bin]['Trans_Error'] )

      if comb:
        for bin in control:
          try:self.Combination_Pred_Table[bin]['Trans'] = comb_test[bin]["MCYield"]/comb[bin]["MCYield"]
          except ZeroDivisionError: pass
          try: control_error =  comb[bin]["SM_Stat_Error"]/comb[bin]["MCYield"] 
          except ZeroDivisionError: control_error = 0
          try :test_error =  comb_test[bin]["SM_Stat_Error"]/comb_test[bin]["MCYield"] 
          except ZeroDivisionError: test_error = 0
          self.Combination_Pred_Table[bin]['Trans_Error'] = self.Combination_Pred_Table[bin]['Trans'] * math.sqrt((control_error*control_error)+(test_error*test_error))
          self.Combination_Pred_Table[bin]['Data_Pred'] = comb[bin]["Data"]
          self.Combination_Pred_Table[bin]['Data_Error'] = sqrt(comb[bin]["Data"]) if comb[bin]["Data"] > 9 else float(eh[int(comb[bin]["Data"])])
          self.Combination_Pred_Table[bin]['Prediction'] = comb[bin]["Data"]*self.Combination_Pred_Table[bin]['Trans']
          self.Combination_Pred_Table[bin]['Data'] = comb_test[bin]["Data"]
          try:self.Combination_Pred_Table[bin]['Pred_Error'] = self.Combination_Pred_Table[bin]['Prediction']*math.sqrt(((self.Combination_Pred_Table[bin]['Data_Error']/self.Combination_Pred_Table[bin]['Data_Pred'])*(self.Combination_Pred_Table[bin]['Data_Error']/self.Combination_Pred_Table[bin]['Data_Pred'])) +((self.Combination_Pred_Table[bin]['Trans_Error']/self.Combination_Pred_Table[bin]['Trans'])*(self.Combination_Pred_Table[bin]['Trans_Error']/self.Combination_Pred_Table[bin]['Trans'])))
          except ZeroDivisionError: self.Combination_Pred_Table[bin]['Pred_Error'] = 0

      #if make_hist : self.Translation_Plots(make_hist,trans_num ,trans_error,self.Settings)
   


  """
  This created the initial root file to be filled with empty histograms. They are in a format that Ted can read from easily. 
  Format_Stats_Root_Output parses the dictionaries and fills the histogram with yields and errors

  """
  def Begin_Stats_Root_Output(self,settings,analysis = ''): 
      Lumi = (self.Settings["Lumo"]*1000)
      directories = []
      if analysis == "Feasibility" : directories = ['had','muon','ll','OSOF','OSSF','SSOF','SSSF']
      if analysis == "RA1": directories = ['had','muon','mumu','phot']
      th1_plots = ["lumiData","lumiMc"]
      th2_plots = ["Data","MCYield"] + self.process #,"TTbar","WJets","Zinv","DY","SingleTop","DiBoson","Photon"] 
            
      self.Stats = r.TFile("./RootFiles/%s_Stats_btag_%s_category_%s.root" %(analysis,self.btag_names[self.number],self.cat_names[self.analysis_category]),"RECREATE")
      print "Making Root File  %s_Stats_btag_%s_category_%s.root" %(analysis,self.btag_names[self.number],self.cat_names[self.analysis_category])

      HT_List = []
      Btag_Slices = [0.0,1.0]
      for num in settings["dirs"] : HT_List.append(int(num.split('_')[0]))
      HT_List.append(int(settings["dirs"][-1].split('_')[0]) + (int(settings["dirs"][-1].split('_')[0]) - int (settings["dirs"][-2].split('_')[0])))
      for dir in directories:
        self.Stats.cd("/")
        self.Stats.mkdir(dir)
        self.Stats.cd(dir)
        for hist in th1_plots:
          plot = TH1F(hist,"",1,0,1)
          if dir == "had":plot.SetBinContent(1,self.Lumi_List["Had"])
          if dir == "muon":plot.SetBinContent(1,self.Lumi_List["Muon"])
          if dir == "mumu":plot.SetBinContent(1,self.Lumi_List["DiMuon"])
          if dir == "phot": plot.SetBinContent(1,self.Lumi_List["Photon"]) 
          plot.Write()
        for second_hist in th2_plots:
          plots = r.TH2D(second_hist,"",len(settings["dirs"]),array.array('d',HT_List),1,array.array('d',Btag_Slices))
          plots.GetXaxis().SetTitle("H_{T} (GeV)")
          plots.GetYaxis().SetTitle("Yield")
          plots.GetZaxis().SetTitle("Yield")
          plots.Write()
      self.Stats.cd("/")   
 
  def Format_Stats_Root_Output(self,dictnames,settings,analysis = ''):
     
      directories = {}
      if analysis == "Feasibility": directories = { "had":self.Had_Yield_Per_Bin, "muon":self.Muon_Yield_Per_Bin, "ll":self.DiLepton_Yield_Per_Bin, "SSOF":self.SSOF_Yield_Per_Bin,"SSSF":self.SSSF_Yield_Per_Bin, "OSOF":self.OSOF_Yield_Per_Bin, "OSSF":self.OSSF_Yield_Per_Bin}
      if analysis == "RA1": directories = { "had":self.Had_Yield_Per_Bin, "muon":self.Muon_Yield_Per_Bin, "mumu":self.DiMuon_Yield_Per_Bin, "phot":self.Photon_Yield_Per_Bin}

      samples = ["Data","MCYield",] + self.process #"TTbar","WJets","Zinv","DY","SingleTop","DiBoson","Photon"] 
      HT_List = []
      for num in settings["dirs"] : HT_List.append(int(num.split('_')[0]))
      HT_List.append(int(settings["dirs"][-1].split('_')[0]) + (int(settings["dirs"][-1].split('_')[0]) - int (settings["dirs"][-2].split('_')[0])))

      for dir in directories:
        for second_hist in directories[dir]:
          for name in samples:
            plots = self.Stats.Get("%s/%s"%(dir,name))
            self.Stats.cd("%s"%dir)
            if name == 'Data' or name == 'MCYield':     
                bin = plots.FindBin(float(second_hist) , 0.5)
                plots.SetBinContent(bin,float(directories[dir][second_hist][name]))
                plots.Write("",r.TObject.kOverwrite)
            else:  
                bin = plots.FindBin(float(second_hist) , 0.5)
                plots.SetBinContent(bin,float(directories[dir][second_hist][name]["Yield"]))
                plots.SetBinError(bin,float(directories[dir][second_hist][name]["Error"]))
                plots.Write("",r.TObject.kOverwrite)

      return 
     

  """
  Tables are make here. Latex_Table produces the output tex table with rows being the information you want to include in the table
  label is what obviously the title of the row and entryFunc is the list which contains the MC yields, process yield you want to display

  """
 
  def Produce_Tables(self,dict,category="",dict2 = ""):
   
      print "\n\nMaking Tables for %s" % category

      if category == "Had_Tables": self.Latex_Table(dict,caption = "Had Yields and MC Breakdown",
            rows = [ {"label": r'''Hadronic yield data''',       "entryFunc":self.MakeList(dict,"Data")},
                    {"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(dict,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(dict,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(dict,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(dict,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(dict,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(dict,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(dict,"DiBoson"),"adddouble":True},])
                    
      if category == "Muon_Tables": self.Latex_Table(dict,caption = "Muon Yields and MC Breakdown",
            rows = [ {"label": r'''Muon yield data''',       "entryFunc":self.MakeList(self.Muon_Yield_Per_Bin,"Data")},
                    {"label": r'''Muon selection MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Pure WJets Ratio''',"entryFunc": self.MakeList(dict,"WJetsRatio","RatioError")},
                    {"label": r'''Pure TTbar Ratio''',"entryFunc": self.MakeList(dict,"TTbarRatio","RatioError")},
                    {"label": r'''Data/MC Ratio''',"entryFunc": self.MakeList(dict,"MCRatio","RatioError"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(self.Muon_Yield_Per_Bin,"DiBoson"),"adddouble":True},])

      if category == "DiMuon_Tables": self.Latex_Table(dict,caption = "DiMuon Yields and MC Breakdown",
            rows = [ {"label": r'''DiMuon yield data''',       "entryFunc":self.MakeList(self.DiMuon_Yield_Per_Bin,"Data")},
                    {"label": r'''DiMuon selection MC''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Pure DY Ratio''',"entryFunc": self.MakeList(dict,"DYRatio","RatioError"),"addhline":True},
                    {"label": r'''Data/MC Ratio''',"entryFunc": self.MakeList(dict,"MCRatio","RatioError"),"addhline":True},
                    {"label": r'''WJets ''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"WJets")},
                    {"label": r'''$t\bar{t}$''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"TTbar")},
                    {"label": r'''Single $t$''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"SingleTop")},
                    {"label": r'''DY ''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"DY")},
                    {"label": r'''Zinv ''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(self.DiMuon_Yield_Per_Bin,"DiBoson"),"adddouble":True},])

      if category == "Photon_Tables": self.Latex_Table(dict,caption = "Photon Yields and MC Breakdown",
            rows = [ {"label": r'''Photon yield data''',       "entryFunc":self.MakeList(self.Photon_Yield_Per_Bin,"Data")},
                    {"label":r'''Photon selection MC''', "entryFunc":self.MakeList(self.Photon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Data/MC Ratio''',"entryFunc": self.MakeList(dict,"MCRatio","RatioError"),"adddouble":True},
                   ])

      if category == "OSOF_Tables": self.Latex_Table(dict,caption = "OSOF Yields and MC Breakdown",
            rows = [ {"label": r'''Hadronic yield data''',       "entryFunc":self.MakeList(dict,"Data")},
                    {"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(dict,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(dict,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(dict,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(dict,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(dict,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(dict,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(dict,"DiBoson"),"adddouble":True},])
     
      if category == "OSSF_Tables": self.Latex_Table(dict,caption = "OSSF Yields and MC Breakdown",
            rows = [ {"label": r'''Hadronic yield data''',       "entryFunc":self.MakeList(dict,"Data")},
                    {"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(dict,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(dict,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(dict,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(dict,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(dict,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(dict,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(dict,"DiBoson"),"adddouble":True},])

      if category == "SSOF_Tables": self.Latex_Table(dict,caption = "SSOF Yields and MC Breakdown",
            rows = [ {"label": r'''Hadronic yield data''',       "entryFunc":self.MakeList(dict,"Data")},
                    {"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(dict,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(dict,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(dict,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(dict,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(dict,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(dict,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(dict,"DiBoson"),"adddouble":True},])

      if category == "SSSF_Tables": self.Latex_Table(dict,caption = "SSSF Yields and MC Breakdown",
            rows = [ {"label": r'''Hadronic yield data''',       "entryFunc":self.MakeList(dict,"Data")},
                    {"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(dict,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''WJets Had MC''',"entryFunc": self.MakeList(dict,"WJets")},
                    {"label": r'''$t\bar{t}$ Had MC''',"entryFunc": self.MakeList(dict,"TTbar")},
                    {"label": r'''Single $t$ Had MC''',"entryFunc": self.MakeList(dict,"SingleTop")},
                    {"label": r'''DY Had MC''',"entryFunc": self.MakeList(dict,"DY")},
                    {"label": r'''Zinv Had MC''',"entryFunc": self.MakeList(dict,"Zinv")},
                    {"label":r'''DiBoson''', "entryFunc":self.MakeList(dict,"DiBoson"),"adddouble":True},])
      
      # ========== RA1 Tables ===============================

      if category == "Total_SM": self.Latex_Table(dict,caption = "Total SM prediction from Muon sample", 
            rows = [{"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(self.Had_Yield_Per_Bin,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''$\mu +$ jets MC''',         "entryFunc":self.MakeList(self.Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error"),"addhline":True},
                    {"label": r'''Translation factor ''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\mu +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''Total SM prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''Hadronic data''',       "entryFunc":self.MakeList(dict,"Data")},])
       
      if category == "Muon_WJet_TTbar": self.Latex_Table(dict,caption = "WJet, TTbar prediction from Muon sample ", 
            rows = [{"label": r'''Hadronic selection MC''',"entryFunc": self.MakeList(self.Had_Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''$\mu +$ jets MC''',         "entryFunc":self.MakeList(self.Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''', "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\mu  +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label": r'''t$\bar{t}$ + W prediction from $\mu +$ jets''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")}])
    
      if category == "Photon_DiMuon": self.Latex_Table(dict,caption = "Photon to predict DiMuon closure test", 
            rows = [{"label": r'''$\mu\bar{\mu} +$ jets MC''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r''' $\gamma +$ jets MC''',         "entryFunc":self.MakeList(self.Photon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\gamma +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''$\mu\bar{\mu} +$ jets prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''$\mu\bar{\mu} +$ jets data''',       "entryFunc":self.MakeList(dict,"Data")},])

      if category == "Photon_Muon": self.Latex_Table(dict,caption = "Photon to predict Muon closure test", 
            rows = [{"label": r'''$\mu + $jets MC''',"entryFunc": self.MakeList(self.Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''$\gamma+$ jets MC''',         "entryFunc":self.MakeList(self.Photon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\gamma +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''$\mu + $jets prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''$\mu +$ jets data''',       "entryFunc":self.MakeList(dict,"Data")},])

      if category == "Di_Muon": self.Latex_Table(dict,caption = "Muon to Predict DiMuon closure test", 
            rows = [{"label": r'''$\mu\bar{\mu} +$ jets MC''',"entryFunc": self.MakeList(self.DiMuon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''$\mu +$ jets MC''',         "entryFunc":self.MakeList(self.Muon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\mu +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''$\mu\bar{\mu} +$ jets prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''$\mu\bar{\mu} +$ jets data''',       "entryFunc":self.MakeList(dict,"Data")},])
       
      if category == "Di_Muon_Zinv": self.Latex_Table(dict,caption = "Zinv prediction from DiMuon sample ", 
            rows = [{"label": r'''Z$\rightarrow\nu\bar{\nu}$ hadronic MC''',"entryFunc": self.MakeList(self.Had_Zinv_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''$\mu\bar{\mu} +$ jets MC''',         "entryFunc":self.MakeList(self.DiMuon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\mu\bar{\mu} +$ jets data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''Z$\rightarrow\nu\bar{\nu}$ prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")}])
     
      if category == "Photon_Zinv": self.Latex_Table(dict,caption = "Zinv prediction from Photon sample", 
            rows = [{"label": r'''Z$\rightarrow\nu\bar{\nu}$ hadronic MC''',"entryFunc": self.MakeList(self.Had_Zinv_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''$\gamma +$ jets MC''',         "entryFunc":self.MakeList(self.Photon_Yield_Per_Bin,"MCYield","SM_Stat_Error")},
                    {"label": r'''Translation factor''',                "entryFunc":self.MakeList(dict,"Trans","Trans_Error")},
                    {"label": r'''$\gamma +$ jet data''',       "entryFunc":self.MakeList(dict,"Data_Pred")},
                    {"label":r'''Z$\rightarrow\nu\bar{\nu}$ prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")}])
  
      if category == "Combined_SM": self.Latex_Table(dict,caption = "Total SM Prediction (Muon + DiMuon)", 
            rows = [{"label": r'''t$\bar{t}$ + W prediction from $\mu +$ jets''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''Z$\rightarrow\nu\bar{\nu}$ prediction from $\mu\mu +$ jets''', "entryFunc":self.MakeList(dict2,"Prediction","Pred_Error")},
                    {"label":r'''Total SM prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error",combined=dict2)},
                    {"label": r'''Hadronic yield from data''',  "entryFunc":self.MakeList(dict,"Data")},])
                   
      if category == "Combined_SM_Photon": self.Latex_Table(dict,caption = "Total SM Prediction (Muon + Photon)", 
            rows = [{"label": r'''$t\bar{t}$ + W prediction from $\mu +$ jets''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error")},
                    {"label": r'''$Z\rightarrow\nu\bar{\nu}$ Prediction from $\gamma +$ jets''', "entryFunc":self.MakeList(dict2,"Prediction","Pred_Error")},
                    {"label":r'''Total SM prediction''', "entryFunc":self.MakeList(dict,"Prediction","Pred_Error",combined=dict2)},
                    {"label": r'''Hadronic yield from data''',  "entryFunc":self.MakeList(dict,"Data")},])
      
 
  def MakeList(self,dict,key,error = "",combined = ""):
      List = []
      for entry in self.bins:

        if key not in self.process:
          if error:
                if dict[entry][error] == 0 and dict[entry][key] == 0:List.append('-')
                else: List.append(self.toString("%4.2f" %(dict[entry][key]+combined[entry][key] if combined else dict[entry][key]))+"  $\pm$  "+ self.toString("%4.2f" % (sqrt((dict[entry][error]*dict[entry][error])+(combined[entry][error]*combined[entry][error])) if combined else dict[entry][error])))
          else: 
                if dict[entry][key] == 0: List.append('-')
                else: List.append(self.toString("%4.2f" %(dict[entry][key]+combined[entry][key] if combined else dict[entry][key])))  

        else:

                if dict[entry][key]["Error"] == 0 and dict[entry][key]["Yield"] == 0:List.append('-')
                else: List.append(self.toString("%4.2f" %dict[entry][key]["Yield"]) +"  $\pm$  "+ self.toString("%4.2f" %dict[entry][key]["Error"]))
      return List  
       
 
  def oneRow(self,label = "", labelWidth = 34, entryList = [], entryWidth = 30, extra = "",addhline = "",adddouble = "") :
  
    s = ""
    s += "\n"+label.ljust(labelWidth)+" & "+" & ".join([(self.toString(entry)).ljust(entryWidth) for entry in entryList])+r"\\ "
    if addhline: s += "\n\hline"
    if adddouble: s+="\n\hline\hline"
    return s 

  def toString(self,item) :
    if type(item) is float : return str(item)
    else : return str(item)

  def Latex_Table(self,dict,rows,caption = ""):
    
        binstable = self.bins
        s = "\n"
        s += r'''\begin{table}[ht!]'''
        s += "\n\caption{%s %s fb$^{-1}$}"%(caption,str(self.Lumi_List["Had"]))
        s += "\n\centering"
        s += "\n"+r'''\footnotesize'''
              
        fullBins = list(binstable)
        num_bins_per_row = 4.0 
        if self.RunOption == "MCNormalisation": num_bins_per_row = 4.0 
        else: pass 
        fullBins = fullBins + ["$\infty$"]
        subnum = int(math.ceil((len(fullBins)-1)/num_bins_per_row))
        
        s += "\n\\begin{tabular}{ "+"c".join("|" for i in range(int(num_bins_per_row+2))) + "}"
        s += "\n\hline"   

        for subTable in range(subnum) :
            start = 0 + subTable*int(num_bins_per_row) 
            stop = 1 + (1+subTable)*int(num_bins_per_row)
            if stop < len(fullBins)+1   : indices = range(start,stop-1)[:int(num_bins_per_row)]
            else : indices = range(start,stop-1)[:(len(fullBins)-1)-start]
            bins = fullBins[start:stop]
            if subTable != 0:
              s += "\n\hline"
      	    s += self.oneRow(label ="$H_{\\textrm{T}}$ Bin (GeV)", entryList = [("%s--%s"%(l, u)) for l,u in zip(bins[:-1], bins[1:])],entryWidth = 25, extra = "[0.5ex]")
            s += "\n\hline"
            for row in rows:
              s += self.oneRow(label = row["label"], entryList = (row["entryFunc"][i] for i in indices) ,entryWidth=row["entryWidth"] if "entryWidth" in row else 25, addhline=True if "addhline" in row else False,adddouble=True if "adddouble" in row else False)    
        s += "\n\hline"
        s += "\n\end{tabular}"
        s += "\n\end{table}"
        s += "\n\n\n\n"
        self.table.write(s)
         
  def Make_Preamble(self):
       s = "\documentclass[english]{article}\n"
       s += "\usepackage[T1]{fontenc}\n"
       s += "\usepackage[latin9]{inputenc}\n"
       s +=  "\usepackage[letterpaper]{geometry}\n"
       s += "\geometry{verbose,bmargin=1cm,lmargin=0.5cm,rmargin=0.5cm}\n"
       s += "\usepackage{float}\n"
       s += "\usepackage{graphicx}\n"
       s += "\usepackage{babel}\n"
       s += "\usepackage{parskip}\n"
       s += "\usepackage{subfigure}\n"
       s += "\usepackage{soul}\n"
       s += "\usepackage{cancel}\n"
       s += "\usepackage{setspace}\n"
       s += "\usepackage{subfig}\n"
       s += "\usepackage{rotating}\n"
       s += "\usepackage{multirow}\n"

       s += "\input{ptdr-definitions}\n"
       s += "\input{symbols}\n"
       s += r'''\begin{document}'''
       s += "\n"
       self.table.write(s) 
          
  def Make_End(self):   
      
      s = "\end{document}"
      self.table.write(s) 

