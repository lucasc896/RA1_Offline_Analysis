#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime
from optparse import OptionParser
import array, ast
from math import *
from plottingUtils import *
from Closure_Tests import *
from Btag_calculation_v3 import *
from Calculation_Template_v4 import *

def MC_Scaler(htbin,alphat_slice,mc_yield,sample = '',error = '',Analysis = '',btagbin = ''):

    if Analysis == "7TeV":	  
        AlphaT_Scale = {"200_0.55":float(0.83),"275_0.55":float(0.83),"325_0.55":float(0.96),"375_0.55":float(0.99),"475_0.55":float(1.0),"575_0.55":1.,"675_0.55":1.,"775_0.55":1.,"875_0.55":1.,"575_0.53":float(0.970),"675_0.53":float(0.970),"775_0.53":float(0.970),"875_0.53":float(0.970),"775_0.52":1.,"875_0.52":1.}
        AlphaT_Error = {"200_0.55":float(0.018),"275_0.55":float(0.018),"325_0.55":float(0.01),"375_0.55":float(0.01),"475_0.55":float(0.048),"575_0.55":float(0.048),"675_0.55":float(0.048),"775_0.55":float(0.048),"875_0.55":float(0.048),"575_0.53":float(0.05),"675_0.53":float(0.05),"775_0.53":float(0.05),"875_0.53":float(0.05),"775_0.52":float(0.207),"875_0.52":float(0.207)}
        DiMuon_Scale = {"200":float(1.0),"275":float(1.0),"325":float(1.0),"375":float(0.95),"475":float(0.95),"575":float(0.96),"675":float(0.96),"775":float(0.96),"875":float(0.97)}
        muon_eff = 0.913
  
    if Analysis == "8TeV":
        AlphaT_Scale = {"150_0.55":float(0.700),"200_0.55":float(0.700),"275_0.55":float(0.90),"325_0.55":float(0.99),"375_0.55":float(0.99),"475_0.55":float(0.99),"575_0.55":1.,"675_0.55":1.,"775_0.55":1.,"875_0.55":1.,"975_0.55":1.,"1075_0.55":1.,"575_0.53":float(0.970),"675_0.53":float(0.970),"775_0.53":float(0.970),"875_0.53":float(0.970),"775_0.52":1.,"875_0.52":1.}
        AlphaT_Error = {"150_0.55":float(0.003),"200_0.55":float(0.003),"275_0.55":float(0.011),"325_0.55":float(0.009),"375_0.55":float(0.011),"475_0.55":float(0.032),"575_0.55":float(0.059),"675_0.55":float(0.059),"775_0.55":float(0.059),"875_0.55":float(0.059),"975_0.55":float(0.059),"1075_0.55":float(0.059),"575_0.53":float(0.05),"675_0.53":float(0.05),"775_0.53":float(0.05),"875_0.53":float(0.05),"775_0.52":float(0.207),"875_0.52":float(0.207)}
        DiMuon_Scale = {"150":float(0.95),"200":float(0.95),"275":float(0.96),"325":float(0.96),"375":float(0.96),"475":float(0.96),"575":float(0.97),"675":float(0.97),"775":float(0.98),"875":float(0.98),"975":float(0.98),"1075":float(0.98)}
        muon_eff = 0.88
   
    scale_factor = htbin +'_'+ alphat_slice
    if mc_yield == 0: return float(mc_yield)
    if sample == "Muon":
      if error:
        return float((error*muon_eff)*math.sqrt(((mc_yield/error)*(mc_yield/error))+((0.01/muon_eff)*(0.01/muon_eff))))
      else:return float(mc_yield*muon_eff)  
    elif sample == "DiMuon":
        if error: return float((error*DiMuon_Scale[htbin])*math.sqrt(((mc_yield/error)*(mc_yield/error))+((0.01/DiMuon_Scale[htbin])*(0.01/DiMuon_Scale[htbin]))))
        else: return float(mc_yield*DiMuon_Scale[htbin])
    elif sample == "Had":
      if alphat_slice == '0.01': scale_factor = htbin +'_0.55'
      if error: 
        return float((error*AlphaT_Scale[scale_factor])*math.sqrt(((mc_yield/error)*(mc_yield/error))+((AlphaT_Error[scale_factor]/AlphaT_Scale[scale_factor])*(AlphaT_Error[scale_factor]/AlphaT_Scale[scale_factor]))))
      else:return float(mc_yield*AlphaT_Scale[scale_factor])
    else: return mc_yield


class Number_Extractor(object):

  def __init__(self,sample_settings,sample_list,number,c_file = "",Triggers = "",Closure = "",Stats = "",AlphaT='',Trans_Plots = '',Calculation = '',Split_Lumi = '',Analysis_category = '',Template = '',Combine = '',Do_sys = '',Working_Point = '',Feasibility = "",RunOption = ""):

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
    self.CombineBins = "True"#Combine
    self.analysis_category = Analysis_category
    self.Lumi_List = {"Had":0,"Muon":0,"DiMuon":0,"Photon":0,"OSOF":0,"OSSF":0,"SSOF":0,"SSSF":0}
    self.btag_names = {"Zero_btags":"eq0","One_btag":"eq1","Two_btags":"eq2","Three_btags":"eq3","More_Than_Zero_btag":"gr0","More_Than_One_btag":"gr1","Inclusive":"Inc","More_Than_Three_btag":"eq4"}
    self.cat_names = {"2":"eq2_and_3","3":"greq4","all":"inclusive"}
  
    self.btagbin = {"Inclusive":1,"Zero_btags":1,"One_btag":2,"Two_btags":3,"Three_btags":4,"More_Than_Three_btag":5}

    print "Analysis conducted for %s" %self.Analysis
    if Split_Lumi == "True":
        print "Multiple Luminosity being used" 
        for key in self.Settings["Multi_Lumi"]:
                print "Sample %s   : Lumi %sfb" %(key , self.Settings["Multi_Lumi"][key])
                self.Lumi_List[key] = self.Settings["Multi_Lumi"][key]
    else: 
        print "Single Luminosity of All Samples is %s fb\n\n" %self.Settings["Lumo"]
        for entry in self.Lumi_List: self.Lumi_List[entry] = self.Settings["Lumo"]
    print self.Lumi_List
    r.gROOT.SetBatch(True)
    if Template: 
        Template_Calc(sample_settings,sample_list,Template,float(self.Settings["Lumo"]),self.Systematic,Working_Point)
        return
    if Calculation: 
      self.return_dict = Btag_Calc(sample_settings,sample_list,Calculation,number,AlphaT,self.Lumi_List,self.Analysis,self.analysis_category).Make_Dict(sample_settings,sample_list,number) 
      self.Form_Vanilla = "Formula"
    else:
      self.Form_Vanilla = "Vanilla"
      self.Create_Dictionary(sample_settings,sample_list)
    self.Prediction_Maker(sample_settings,self.return_dict)

  def Create_Dictionary(self,settings,samples):
         print "In uncorrected yields"
         table_entries = "{" 
         for key,fi in sorted(samples.iteritems()):
           i = 0
           for dir in settings['dirs']:
              fixed_dir = dir
              for alphat in settings['AlphaTSlices']:
                dir = fixed_dir
                lower = alphat.split('_')[0]
                higher = alphat.split('_')[1]
                table_entries += "\t\"%s_%d\"  : "%(key,i)
                i+=1
                table_entries += "{\"HT\":\"%s\","%(dir.split('_')[0])
                for histName in settings['plots']:
                    histName = str(histName+self.analysis_category) 
                    checkht = dir
                    dir = fi[1]+dir
                    Luminosity = self.Lumi_List[fi[3]]
                    normal =  GetSumHist(File = ["%s.root"%fi[0]], Directories = [dir], Hist = histName, Col = r.kBlack, Norm = None if "n" == key[0] else [float(Luminosity*1000)/100.], LegendText = "nBtag")  
                    normal.HideOverFlow()
                    err = r.Double(0.0)
                    normal.hObj.IntegralAndError(self.btagbin[self.number],normal.hObj.GetNbinsX(),err)
                    table_entries +=" \"Yield\": %.3e ,\"Error\":\"%s\",\"SampleType\":\"%s\",\"Category\":\"%s\",\"AlphaT\":%s},\n"%((normal.hObj.GetBinContent(self.btagbin[self.number]) if self.number not in ["More_Than_Three_btag","Inclusive"] else normal.hObj.Integral(self.btagbin[self.number],normal.hObj.GetNbinsX())),(normal.hObj.GetBinError(self.btagbin[self.number]) if self.number not in ["More_Than_Three_btag","Inclusive"]  else err),fi[2],fi[3],lower)
                    normal.a.Close()
         
         table_entries +="}"
         self.return_dict = ast.literal_eval(table_entries)
         return self.return_dict

  def Prediction_Maker(self,settings,dict):

      
      self.bins = tuple(settings["bins"]+["200_upwards"])
      entries = ('Data','MCYield','Tot_Error','SM_Stat_Error','TTbar','WJets','Zinv','DY','DiBoson','SingleTop','Photon','Btag','SampleName','JetCategory','AlphaT')
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
            for SM in self.process:
                dicto[key][SM] = dict.fromkeys(yields,0) 
                dicto[key][SM]['Process_Error'] = []

        meanbin_dict = {"150":178.2,"200":235.2,"275":297.5,"325":347.5,"375":416.4,"475":517.3,"575":618.4,"675":716.9,"775":819.9,"875":919.,"975":1019.,"1075":1289.}
 
        for entry,fi in dict.iteritems():
          
           
          if str(fi['AlphaT']) == str(slices).split('_')[0] :
           
            """ 
            if dict[entry]["SampleType"] in ["Zinv","DY","Photon"]:
             
              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*0.9103)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*0.9103)          
 
            if dict[entry]["SampleType"] in ["WJets"]:
             
              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*0.8785)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*0.8785)

            if dict[entry]["SampleType"] in ["TTbar","SingleTop","DiBoson"]:

              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*1.205)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*1.205)
            
            
            """
            
            midht = meanbin_dict[dict[entry]["HT"]]

            if dict[entry]["SampleType"] in ["Photon"]:

              scalefactor = 0.996212 - 0.0003764*(midht) # ISR PU 1.14 sf
              #scalefactor = 0.8716 - 0.00005568*(midht) # IS PU Parton  1.15 sf
              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*scalefactor*1.14)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*scalefactor*1.14)          


            if dict[entry]["SampleType"] in ["Zinv","DY"]:
            
              scalefactor = 0.996212 - 0.0003764*(midht) # ISR PU 1.05 sf
              #scalefactor = 0.8716 - 0.00005568*(midht) # IS PU Parton  1.05 sf
              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*scalefactor*1.05)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*scalefactor*1.05)          
 
            if dict[entry]["SampleType"] in ["WJets"]:
            
              scalefactor = 0.989713 - (0.00034799*midht) # ISR PU 0.95 sf
              #scalefactor = 0.90123 - 0.0000971045*midht # ISR PU Parton 0.95 sf
              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*scalefactor*0.95)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*scalefactor*0.5)

            if dict[entry]["SampleType"] in ["TTbar"]:

              scalefactor = 1.132 - (0.000431469*midht) # sf 1.03

              dict[entry]["Yield"] = (float(dict[entry]["Yield"])*scalefactor*1.03)
              dict[entry]["Error"] =  (float(dict[entry]["Error"])*scalefactor*1.03)
           

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

        for bin in self.Muon_Yield_Per_Bin: 
          for sample in dictionaries: 
            try:  sample[bin]["SM_Stat_Error"] = math.sqrt(reduce(lambda x,y : x+y,map(lambda x: x*x, sample[bin]["Tot_Error"])))
            except TypeError: pass


        if self.Trigger_Scaling == "True":
          print "Apply MC Correction For Scaling"
          for bin in self.Muon_Yield_Per_Bin:
             for sample in dictionaries:
               
               sample[bin]["MCYield"] = MC_Scaler(bin,sample[bin]['AlphaT'],sample[bin]["MCYield"],sample = sample[bin]["SampleName"],Analysis = self.Analysis,btagbin = self.number )
               sample[bin]["SM_Stat_Error"] = MC_Scaler(bin,sample[bin]['AlphaT'],sample[bin]["SM_Stat_Error"],sample = sample[bin]["SampleName"],error = sample[bin]["MCYield"],Analysis = self.Analysis, btagbin = self.number )
               
               for SM in self.process:
               
                 sample[bin][SM]["Yield"] = MC_Scaler(bin,sample[bin]['AlphaT'],sample[bin][SM]["Yield"],sample = sample[bin]["SampleName"],Analysis = self.Analysis,btagbin = self.number )
                 sample[bin][SM]["Error"] = MC_Scaler(bin,sample[bin]['AlphaT'],sample[bin][SM]["Error"],sample = sample[bin]["SampleName"],error = sample[bin][SM]["Yield"],Analysis = self.Analysis, btagbin = self.number )

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
            
              self.Table_Prep(self.Muon_Yield_Per_Bin,self.Had_Muon_Yield_Per_Bin,make_hist = "Muon")
              self.Produce_Tables(self.Dict_For_Table,category = "Muon")
            
              self.Table_Prep(self.Photon_Yield_Per_Bin,self.Had_Zinv_Yield_Per_Bin,make_hist = "Photon_Zinv")
              self.Produce_Tables(self.Dict_For_Table,category = "Photon_Zinv")
            
              self.Table_Prep(self.DiMuon_Yield_Per_Bin,self.Had_Zinv_Yield_Per_Bin,make_hist = "Di_Muon_Zinv")
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
        if self.Make_Root_Stats_File == "True":
          self.Begin_Stats_Root_Output(self.Settings,analysis = analysis_type)
          self.Format_Stats_Root_Output(dictionaries,settings, analysis = analysis_type)
        if self.Make_Closure_Tests == "True" :self.Jad_Output(jad_dictionaries)    

  def Jad_Output(self,input):
    for file in input: 
        self.c_file.append(file)


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
      Btag_Slices = [0,1,2,3,4,5]
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

