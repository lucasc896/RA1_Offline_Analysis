#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys
import glob, errno
from time import strftime
from optparse import OptionParser
import array, ast
from ROOT import TMatrixD
from math import *
from plottingUtils import *

class Template_Calc(object):

     def __init__(self,settings,samples,jet_mult,lumo,Do_Sys = '',Working_Point = ''):

         self.Lumo = lumo
         self.Working_Point = Working_Point
         self.settings = settings
         self.fitparam = 3
         self.totaljetmultiplicity = jet_mult
         #self.FitType = "Simulataneous"
         self.FitType = "Individual"
         self.DoPull = "False"

         r.gROOT.ProcessLine(".L tdrstyle.C")
         r.setstyle()
         r.gROOT.SetBatch(True)
         r.gStyle.SetOptStat(0)

         for num,bin in enumerate(self.settings["dirs"]):
             self.c1= r.TCanvas("Fit Result", "Fit Result",0,0,900,600)
             self.c1.SetLogy(0)

             #======= Dictionaries are made here =============================
             self.current_htbin = bin
             self.bins = ('2','3','4','5')
             entries  = ('Data','Data_Err','Data_Err_Matrix','Z0','Z2','Plus','Minus','Normal','FitResult','FitError')
             syst_dict = ('Plus','Minus','Normal')
             template_entries = ( 'Full_Template','Theta','ndof','FitCovariance')
             btag_mc = ('Btag_Efficiency','Mistag_Efficiency','Btag_Error','Mistag_Error','Ctag_Efficiency','Ctag_Error','Btag_Efficiency_plus','Mistag_Efficiency_plus','Btag_Efficiency_minus','Mistag_Efficiency_minus','Ctag_plus','Ctag_minus'  )
             self.Data_Dict = dict.fromkeys(self.bins)
             self.MC_Dict = dict.fromkeys(self.bins)
             dictionaries = [self.Data_Dict,self.MC_Dict]

             for dicto in dictionaries:
                for key in self.bins:
                   dicto[key] = dict.fromkeys(entries,0)
                   dicto[key]['Data'] = []
                   dicto[key]['Data_Err'] = []
                   dicto[key]['Data_Err_Matrix'] = []
                   dicto[key]['FitError'] = []
                   dicto[key]['FitResult'] = []

                   
             for dicto in dictionaries:
                for key in self.bins:
                   dicto[key]["Z0"] = dict.fromkeys(btag_mc,0)
                   dicto[key]["Z2"] = dict.fromkeys(btag_mc,0)

             for dicto in dictionaries:
                for key in self.bins:
                   dicto[key]["Plus"] = dict.fromkeys(template_entries,0)
                   dicto[key]["Minus"] = dict.fromkeys(template_entries,0)
                   dicto[key]["Normal"] = dict.fromkeys(template_entries,0)
                   for j in syst_dict:
                      dicto[key][j]['Theta'] = []
                      dicto[key][j]['Full_Template'] = []
       
             #=============================================================================

             #========================= Btag/Mistag Rates are calculated =================
             for numjets in jet_mult:
               for key,fi in sorted(samples.iteritems()):
                 if fi[2] not in ["Data","MC"]:
                    for dicto in dictionaries: 
                        if dicto == self.Data_Dict : self.Btag_Rate(samples[key],self.current_htbin,numjets,dicto,"Data")
                        else :  self.Btag_Rate(samples[key],self.current_htbin,numjets,dicto,"MC")
             #============================================================================

             #====================== Templates are generated / Data Extracted =============

             for numjets in jet_mult:
               for key,fi in sorted(samples.iteritems()):
                 if fi[2] not in ["Data","MC"]:
                    for dicto in dictionaries:
                        if dicto == self.Data_Dict: self.Generate_Templates(samples[key],self.current_htbin,numjets,dicto,"Data")
                        else: self.Generate_Templates(samples[key],self.current_htbin,numjets,dicto,"MC")
                 self.sample_type = fi[1]
                 if fi[2] =="Data": self.Extract_Data(samples[key],self.current_htbin,numjets,self.Data_Dict,fi[2])
                 if fi[2] =="MC": self.Extract_Data(samples[key],self.current_htbin,numjets,self.MC_Dict,fi[2])
  
             #============================================================================

                          #===================== Do Fits  =========================================
             if self.FitType == "Individual":
                for jetnum in jet_mult:
                     for suffix in ['Normal','Plus','Minus']: 
                        #self.DoFit(self.fitparam,jetnum,suffix,self.Data_Dict,"Data")
                        self.DoFit(self.fitparam,jetnum,suffix,self.MC_Dict,"MC")
                     #self.MakeFinalFit(self.Data_Dict,"Normal",jetnum,"Data")
                     self.MakeFinalFit(self.MC_Dict,"Normal",jetnum,"MC")
                     if self.DoPull == "True" : self.Pull_Plots( self.MC_Dict,jetnum )
                #self.RatioPlots(dictionaries)

             if self.FitType == "Simulataneous":
                for jetnum in jet_mult:
                  for suffix in ['Normal','Plus','Minus']: 
                        self.DoFit(self.fitparam,jetnum,suffix,self.Data_Dict,"Data",combine = "True")
                  self.DoFit(self.fitparam,jetnum,"Normal",self.MC_Dict,"MC",combine = "True")
                  self.MakeFinalFit(self.Data_Dict,"Normal",jetnum,"Data")
                  self.MakeFinalFit(self.MC_Dict,"Normal",jetnum,"MC")
             #===========================================================================

             #==================  Make Plots/ Tables  =========================================            
             #self.Produce_Yield_Table(self.Data_Dict,"Data")
             #self.Produce_Yield_Table(self.MC_Dict,"MC")
             #========================================================================
             """
             #print self.MC_Dict["2"]["Normal"]["Full_Template"]
             #print "================="
             #print self.MC_Dict["2"]["Z0"]
             #print "================="
             #print self.MC_Dict["2"]["Z2"]
             """             

     def Produce_Yield_Table(self,Dict,isdata):

        for i in self.totaljetmultiplicity:

           self.Table = open("Yield_Table_For_%s_%s_HTbin_%s_jetmult_%s.tex"%(isdata,self.Working_Point,self.current_htbin,i) ,'w')
           self.Tabletxt = open("Yield_Table_For_%s_%s_HTbin_%s_jetmult_%s.txt"%(isdata,self.Working_Point,self.current_htbin,i) ,'w')

           bins = [0,1,2,3,4] 
           total_yields = [[],[],[]]
           temp_yields = [[],[],[]]

           s = "\n"
           s += r'''\begin{table}[ht!]'''
           s += "\n\caption{%s }"%self.current_htbin
           s += "\n\centering"
           s += "\n"+r'''\footnotesize'''
           s += "\n\\begin{tabular}{ |c|c|c|c|c| }"
           s += "\n\hline"    
           s += self.oneRow(label ="Num Btags", entryList = [("%s"%(l)) for l in (bins)], extra = "[0.5ex]")
           t = ""

           for j in range(0,5):#Dict[self.totaljetmultiplicity[-1]]["FitResult"].GetNbinsX()):

             mc_error_plus = 0
             mc_error_minus = 0
             try:mc_error_plus = sqrt(Dict[i]["FitError"][0][j])
             except IndexError: pass
             try:mc_error_minus =sqrt(Dict[i]["FitError"][1][j])
             except IndexError: pass

             t += "\n  %s btags \n"%j
             t += "MC Yield : %s +- %s \n " %(Dict[i]["Data"][j],Dict[i]["Data_Err"][j])
             t += "Template Yield: %s +  %s - %s \n " %( Dict[i]["FitResult"].GetBinContent(j+1) , mc_error_plus ,mc_error_minus )

             total_yields[0].append( Dict[i]["Data"][j] )
             total_yields[1].append(Dict[i]["Data_Err"][j])
             temp_yields[0].append(Dict[i]["FitResult"].GetBinContent(j+1))
             temp_yields[1].append(mc_error_plus)
             temp_yields[2].append(mc_error_minus)

           s += self.oneRow(label = "Data", entryList = ( self.MakeList(total_yields)),entryWidth= 30, addhline=False,adddouble=False) 
           s += self.oneRow(label = "Template", entryList = ( self.MakeList(temp_yields,errors = "True")),entryWidth= 30, addhline=False,adddouble=False)   
 
           s += "\n\hline"
           s += "\n\end{tabular}"
           s += "\n\end{table}"
           s += "\n\n\n\n"

           self.Table.write(s)
           self.Tabletxt.write(t)
        
        self.Table = open("Yield_Table_For_%s_%s_HTbin_%s.tex"%(isdata,self.Working_Point,self.current_htbin) ,'w')
        self.Tabletxt = open("Yield_Table_For_%s_%s_HTbin_%s.txt"%(isdata,self.Working_Point,self.current_htbin) ,'w')

        bins = [0,1,2,3,4] 
        total_yields = [[],[],[]]
        temp_yields = [[],[],[]]
        
        s = "\n"
        s += r'''\begin{table}[ht!]'''
        s += "\n\caption{%s }"%self.current_htbin
        s += "\n\centering"
        s += "\n"+r'''\footnotesize'''
        s += "\n\\begin{tabular}{ |c|c|c|c|c| }"
        s += "\n\hline"    
        s += self.oneRow(label ="Num Btags", entryList = [("%s"%(l)) for l in (bins)], extra = "[0.5ex]")
        t = ""

        for j in range(0,5):#Dict[self.totaljetmultiplicity[-1]]["FitResult"].GetNbinsX()):
       
             data = 0
             data_error = 0
             mc = 0
             mc_error_plus = 0
             mc_error_minus = 0

             for i in self.totaljetmultiplicity:
                data += Dict[i]["Data"][j]
                data_error += pow(Dict[i]["Data_Err"][j],2)
                mc += Dict[i]["FitResult"].GetBinContent(j+1)
                try:mc_error_plus += Dict[i]["FitError"][0][j]
                except IndexError: pass
                try:mc_error_minus +=Dict[i]["FitError"][1][j]
                except IndexError: pass
             if isdata == "Data" :data_error = self.Poission(data)
             else: data_error = sqrt(data_error)
             mc_error_plus = sqrt(mc_error_plus)
             mc_error_minus = sqrt(mc_error_minus)

             total_yields[0].append(data)
             total_yields[1].append(data_error)
             temp_yields[0].append(mc)
             temp_yields[1].append(mc_error_plus)
             temp_yields[2].append(mc_error_minus)
             t += "\n  %s btags \n"%j
             t += "MC Yield : %s +- %s \n " %(data,data_error)
             t += "Template Yield: %s +  %s - %s \n " %(mc,mc_error_plus,mc_error_minus)

        s += self.oneRow(label = "Data", entryList = ( self.MakeList(total_yields)),entryWidth= 30, addhline=False,adddouble=False) 
        s += self.oneRow(label = "Template", entryList = ( self.MakeList(temp_yields,errors = "True")),entryWidth= 30, addhline=False,adddouble=False)   
        s += "\n\hline"
        s += "\n\end{tabular}"
        s += "\n\end{table}"
        s += "\n\n\n\n"

        self.Table.write(s)
        self.Tabletxt.write(t)
        
     def toString(self,item) :
        if type(item) is float : return str(item)
        else : return str(item)

     def MakeList(self,dict,errors = ''):
      List = []
      for num,entry in enumerate(dict[0]):
        if errors == "True":
          if dict[0][num] == 0: List.append('-')
          else: List.append(self.toString("%4.2f + %4.2f - %4.2f" %(dict[0][num],dict[1][num],dict[2][num])))  

        else:
          if dict[0][num] == 0: List.append('-')
          else: List.append(self.toString("%4.2f +- %4.2f " %(dict[0][num],dict[1][num])))  
      return List  

     def oneRow(self,label = "", labelWidth = 23, entryList = [], entryWidth = 30, extra = "",addhline = "",adddouble = "") :
        
        s = ""
        s += "\n"+label.ljust(labelWidth)+" & "+" & ".join([(self.toString(entry)).ljust(entryWidth) for entry in entryList])+r"\\ "
        if addhline: s += "\n\hline"
        if adddouble: s+="\n\hline\hline"
        return s 

     def RatioPlots(self,Dicts):

         self.c1.cd(1)

         names = ["Data","MC"]
         ratio_holder = []

         for num,dictos in enumerate(Dicts):
            
            inputname =  names[num]
            plot = r.TH1F("" ,"",len(self.totaljetmultiplicity),float(self.totaljetmultiplicity[0]),float(self.totaljetmultiplicity[-1])+1)

            for num,jet in enumerate(self.totaljetmultiplicity):
                 plot.SetBinContent(int(num)+1,1,float(dictos[jet]["Normal"]["Theta"][0]/dictos[jet]["Normal"]["Theta"][1]))
                 plot.SetBinError(int(num)+1,1,float(dictos[jet]["Normal"]["Theta"][0]/dictos[jet]["Normal"]["Theta"][1])*sqrt( pow(float(dictos[jet]["Normal"]["FitError_0"]/dictos[jet]["Normal"]["Theta"][0]),2)+ pow(float(dictos[jet]["Normal"]["FitError_2"]/dictos[jet]["Normal"]["Theta"][1]),2) - (2*( (  dictos[jet]["Normal"]["FitError_0"]*dictos[jet]["Normal"]["FitError_2"]  )/( dictos[jet]["Normal"]["Theta"][1]*dictos[jet]["Normal"]["Theta"][0] ) )* dictos[jet]["Normal"]["FitCovariance"]      )))

            plot.Draw()
            ratio_holder.append(plot)
            self.c1.SaveAs("%s_WP_Ratio_Z0_Z2_in_%s_HTbin_%s.png"%(self.Working_Point,inputname,self.current_htbin))

         ratio_holder[0].Divide(ratio_holder[1])
         ratio_holder[0].Draw()
         self.c1.SaveAs("%s_WP_Ratio_Z0_Z2_Data_vs_MC_HTbin_%s.png"%(self.Working_Point,self.current_htbin))

     def Pull_Plots(self,Dict,jetnum):

         R1 = TRandom3(0)
         Z0fitresult = TH1D("Z0fitresult", ";Z=0 pull;", 100, -5.05, 4.95)
         Z2fitresult = TH1D("Z2fitresult", ";Z=2 pull;", 100, -5.05, 4.95)
         relerr = 1.0
         tot_toys=100000
         r.gStyle.SetOptStat(1111)

         for i in range(tot_toys): 
            if i in [0,int(tot_toys*0.2),int(tot_toys*0.4),int(tot_toys*0.6),int(tot_toys*0.8),int(tot_toys-1)]:
                print "At Toy %s" %i
            
            data_toy = [] 
            mc_templates = []
            data_toy_error = Dict[jetnum]["Data_Err_Matrix"]
            for num,j in enumerate(Dict[jetnum]["Data"][:self.fitparam]): data_toy.append(R1.Gaus(Dict[jetnum]["Data"][num],relerr*Dict[jetnum]["Data_Err"][num]))

            for temp1,temp2 in zip(Dict[jetnum]["Normal"]["Full_Template"][0][:self.fitparam],Dict[jetnum]["Normal"]["Full_Template"][1][:self.fitparam]):
                mc_templates.append(temp1)
                mc_templates.append(temp2)   

            A = TMatrixD(self.fitparam,2,array.array('d',mc_templates))          
            Y = TMatrixD(self.fitparam,1,array.array('d',data_toy))  
            V = TMatrixD(self.fitparam,self.fitparam,array.array('d',data_toy_error))

            AT = TMatrixD(2,self.fitparam) 
            AT.Transpose(A) 

            Vinv = TMatrixD(V)
            Vinv.Invert()
        
            # Now lets calculate C1,C2, S1,S2 and theta

            C1 = TMatrixD(self.fitparam,2)
            C1.Mult(Vinv,A)
            C2 = TMatrixD(2,2)
            C2.Mult(AT,C1)
        
            S1 = TMatrixD(self.fitparam,1)
            S1.Mult(Vinv,Y)
            S2 = TMatrixD(2,1)
            S2.Mult(AT,S1) 

            Cinv = TMatrixD(C2)
            Cinv.Invert()

            Theta = TMatrixD(2,1)
            Theta.Mult(Cinv,S2)

            try: Z0fitresult.Fill((Theta(0,0) - Dict[jetnum]["Normal"]["Theta"][0])/sqrt(Cinv(0,0)))
            except ValueError: print "Passing" 
            try:Z2fitresult.Fill((Theta(1,0) - Dict[jetnum]["Normal"]["Theta"][1])/sqrt(Cinv(1,1)))
            except ValueError: print "Passing"

         Z0fitresult.Draw()
         self.c1.SaveAs("Pull_Plot_Z0_HTbin_%s_jet_mult_%s_num_param_%s.png"%(self.current_htbin,jetnum,self.fitparam))
         Z2fitresult.Draw()
         self.c1.SaveAs("Pull_Plot_Z2_HTbin_%s_jet_mult_%s_num_param_%s.png"%(self.current_htbin,jetnum,self.fitparam))

     def MakeFinalFit(self,Dict,suffix,jetnum,isdata):

        num_bins = int(jetnum)+1
        if jetnum == "5": num_bins = 5
        fitresult = TH1D("fitresult", ";n_{b}^{reco};Entries", num_bins, -0.50, (num_bins-0.5))
        data_hist = TH1D("data", ";n_{b}^{reco};Entries", num_bins, -0.50, (num_bins-0.5))
        template0 = TH1D("template0", ";n_{b}^{reco};Entries", num_bins, -0.50, (num_bins-0.5))
        template2 = TH1D("template2", ";n_{b}^{reco};Entries", num_bins, -0.50, (num_bins-0.5))
       
        for i in range(0,int(jetnum)+1):
       
          data_hist.Fill(i,Dict[jetnum]["Data"][i])
          data_hist.SetBinError(i+1,Dict[jetnum]["Data_Err"][i])
    
        for num in range(0,len( Dict[jetnum][suffix]["Full_Template"][1])): 
         
          template0.Fill(num, Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]))
          template2.Fill(num, Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))
          fitresult.Fill(num, Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]) + Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))
          fitresult.SetBinError(num+1,sqrt(pow((Dict[jetnum][suffix]["FitError_0"])*Dict[jetnum][suffix]["Full_Template"][0][num],2)+(pow(Dict[jetnum][suffix]["FitError_2"]*Dict[jetnum][suffix]["Full_Template"][1][num],2))+(2*Dict[jetnum][suffix]["Full_Template"][0][num]*Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["FitCovariance"]))))

        totresult = TGraphAsymmErrors(fitresult)
        totup = []
        totdown = []

        if isdata == "Data" or isdata == "MC":
           for num in range(0,len( Dict[jetnum][suffix]["Full_Template"][1])):
               
                totresult.SetPointEYhigh(num, sqrt(pow(((Dict[jetnum]["Plus"]["Full_Template"][0][num]*float(Dict[jetnum]["Plus"]["Theta"][0]) + Dict[jetnum]["Plus"]["Full_Template"][1][num]*float(Dict[jetnum]["Plus"]["Theta"][1])) -  (Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]) + Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))),2)+ pow(fitresult.GetBinError(num+1) ,2) ))
                totresult.SetPointEYlow(num, sqrt(pow(((Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]) + Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))  - (Dict[jetnum]["Minus"]["Full_Template"][0][num]*float(Dict[jetnum]["Minus"]["Theta"][0]) + Dict[jetnum]["Minus"]["Full_Template"][1][num]*float(Dict[jetnum]["Minus"]["Theta"][1]))),2) + pow(fitresult.GetBinError(num+1) ,2)))
                totup.append(pow(((Dict[jetnum]["Plus"]["Full_Template"][0][num]*float(Dict[jetnum]["Plus"]["Theta"][0]) + Dict[jetnum]["Plus"]["Full_Template"][1][num]*float(Dict[jetnum]["Plus"]["Theta"][1])) -  (Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]) + Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))),2)+ pow(fitresult.GetBinError(num+1) ,2))
                totdown.append(pow(((Dict[jetnum][suffix]["Full_Template"][0][num]*float(Dict[jetnum][suffix]["Theta"][0]) + Dict[jetnum][suffix]["Full_Template"][1][num]*float(Dict[jetnum][suffix]["Theta"][1]))  - (Dict[jetnum]["Minus"]["Full_Template"][0][num]*float(Dict[jetnum]["Minus"]["Theta"][0]) + Dict[jetnum]["Minus"]["Full_Template"][1][num]*float(Dict[jetnum]["Minus"]["Theta"][1]))),2) + pow(fitresult.GetBinError(num+1) ,2))

        else:

           for num in range(0,len( Dict[jetnum][suffix]["Full_Template"][1])):

                totup.append(pow(fitresult.GetBinError(num+1) ,2))
                totdown.append( pow(fitresult.GetBinError(num+1) ,2))

        temp0 = TGraph(template0)
        temp2 = TGraph(template2)
        totresult.SetFillColor(1)
        totresult.SetFillStyle(3003)
        data_hist.GetYaxis().SetTitle("Events");
        data_hist.GetXaxis().SetTitle("Num B-tags")
        data_hist.SetTitle("Final Simultaneous fit to %s , Num Jets = %s" %(isdata,jetnum))
        data_hist.SetLineColor(kBlack)
        data_hist.SetLineWidth(3)
        if isdata == "MC" :data_hist.SetMinimum(0.001)
        else: data_hist.SetMinimum(0.1)
        data_hist.Draw("pe1x0")
        totresult.SetLineWidth(2)
        fitresult.Draw("lsamex0")
        totresult.Draw("samel2")
        temp0.SetLineColor(kRed)
        temp0.SetLineWidth(2)
        temp0.Draw("samel")
        temp2.SetLineColor(kBlue)
        temp2.SetLineWidth(2)
        temp2.Draw("samel")
        data_hist.SetMarkerStyle(20)
        data_hist.Draw("samepe1x0")
        self.TextBox(Dict[jetnum][suffix]["Chi_2"],Dict[jetnum][suffix]["ndof"],label="Pre")
        
        err = r.Double(0.0)
        toterr = r.Double(0.0)
        errstat = r.Double(0.0)
        toterrstat = r.Double(0.0)
        fitresult.IntegralAndError(4,8,errstat)
        fitresult.IntegralAndError(4,8,toterrstat)
        data_hist.IntegralAndError(4,8,err)
        data_hist.IntegralAndError(0,8,toterr)

        if jetnum != "2":self.Template_Yield(data_hist.Integral(4,5), "Data nb >= 3",stat_error = err,xaxis = 0.45,yaxis = 0.80)
        self.Template_Yield(data_hist.Integral(), "Total Data ",stat_error = toterr,xaxis = 0.45,yaxis = 0.72)

        if isdata == "Data" or isdata == "MC":
                if jetnum != "2":
                  signal_syst_up = sqrt(reduce(lambda x,y : x+y,totup[3:]))
                  signal_syst_down = sqrt(reduce(lambda x,y : x+y,totdown[3:]))
                tot_syst_up = sqrt(reduce(lambda x,y : x+y,totup))
                tot_syst_down = sqrt(reduce(lambda x,y : x+y,totdown))

                if jetnum != "2": self.Template_Yield(fitresult.Integral(4,5), "Template nb >=%s"%self.fitparam,stat_error = signal_syst_up,syst_error = signal_syst_down, xaxis = 0.45,yaxis = 0.76)
                self.Template_Yield(fitresult.Integral(), "Total Template",stat_error = tot_syst_up,syst_error = tot_syst_down, xaxis = 0.45,yaxis = 0.68)

        else: 
            if jetnum != "2":self.Template_Yield(fitresult.Integral(4,5), "Template nb >=%s"%self.fitparam,stat_error = errstat,xaxis = 0.45,yaxis = 0.76)
            self.Template_Yield(fitresult.Integral(), "Total Template ",stat_error = toterrstat,xaxis = 0.45,yaxis = 0.68)

        Dict[jetnum]["FitError"].append(totup)
        Dict[jetnum]["FitError"].append(totdown)
        Dict[jetnum]["FitResult"] = fitresult

        self.c1.SaveAs("Final_Fit_To_%s_%s_%s_HTBin_%s%s_jet_mult_%s.png"%(isdata,suffix,self.Working_Point,self.sample_type,self.current_htbin,jetnum))

     def Template_Yield(self,tot,name,stat_error='',syst_error='' ,xaxis = '',yaxis = ''):
        Textbox = TLatex()
        Textbox.SetNDC()
        Textbox.SetTextAlign(12)
        Textbox.SetTextSize(0.04)
        if syst_error: Textbox.DrawLatex(xaxis,yaxis, "%s: %4.2f +%4.3f -%4.3f " %(name,tot,stat_error,syst_error))
        else:  Textbox.DrawLatex(xaxis,yaxis, "%s: %4.2f +- %4.3f" %(name,tot,stat_error))
   
     def DoFit(self,num_param,jet_mult,suffix,Dict,isdata,combine = ''):

        self.c1.cd(1)
        sing_param = num_param

        if combine == "True": 
              num_param = num_param * len(self.totaljetmultiplicity)
              fit_type = self.totaljetmultiplicity
              data = []
              data_err = []
              data_error_matrix = [0.0]*int(pow(self.fitparam*len(self.totaljetmultiplicity),2))
              for numberjet in self.totaljetmultiplicity: 
                data += Dict[numberjet]["Data"][:sing_param]
                data_err += Dict[numberjet]["Data_Err"][:sing_param]

              for i in range(0,self.fitparam*len(self.totaljetmultiplicity)):
                  for j in range(0, self.fitparam*len(self.totaljetmultiplicity)):
                    counter = (i*self.fitparam*len(self.totaljetmultiplicity))+j
                    if (i== j): data_error_matrix[counter] =(pow(data_err[i],2))
 
        else: 
              fit_type = [jet_mult]
              data = Dict[jet_mult]["Data"][:num_param]
              data_err = Dict[jet_mult]["Data_Err"][:num_param]
              data_error_matrix = Dict[jet_mult]["Data_Err_Matrix"]

        fitresult = TH1D("fitresult", ";n_{b}^{reco};Entries", num_param, -0.50, (num_param-0.5))
        data_hist = TH1D("data", ";n_{b}^{reco};Entries", num_param, -0.50, (num_param-0.5))
        template0 = TH1D("template0", ";n_{b}^{reco};Entries", num_param, -0.50, (num_param-0.5))
        template2 = TH1D("template2", ";n_{b}^{reco};Entries", num_param, -0.50, (num_param-0.5))

        print "Making fit for %s parameters" %num_param

        mc_templates = []

        for jetmult in fit_type: 
          for temp1,temp2 in zip(Dict[jetmult][suffix]["Full_Template"][0][:sing_param],Dict[jetmult][suffix]["Full_Template"][1][:sing_param]):
            mc_templates.append(temp1)
            mc_templates.append(temp2)   
 
        A = TMatrixD(num_param,2,array.array('d',mc_templates))          
        Y = TMatrixD(num_param,1,array.array('d',data))  
        V = TMatrixD(num_param,num_param,array.array('d',data_error_matrix)) 
        
        AT = TMatrixD(2,num_param) 
        AT.Transpose(A) 

        Vinv = TMatrixD(V)
        Vinv.Invert()
        
        C1 = TMatrixD(num_param,2)
        C1.Mult(Vinv,A)
        C2 = TMatrixD(2,2)
        C2.Mult(AT,C1)
        
        S1 = TMatrixD(num_param,1)
        S1.Mult(Vinv,Y)
        S2 = TMatrixD(2,1)
        S2.Mult(AT,S1) 

        Cinv = TMatrixD(C2)
        Cinv.Invert()
        Cinv.Print()
        Dict[jet_mult][suffix]["FitError_0"]=sqrt(Cinv(0,0))
        Dict[jet_mult][suffix]["FitError_2"]=sqrt(Cinv(1,1))
        Dict[jet_mult][suffix]["FitCovariance"]= (Cinv(1,0))
    
        Theta = TMatrixD(2,1)
        Theta.Mult(Cinv,S2)
        Theta.Print()
        
        #============== Make Plots =================
        for i in range(0,len(mc_templates),2): 
          g = i/2
          template0.Fill(g, mc_templates[i]*Theta(0,0));
          template2.Fill(g, mc_templates[i+1]*Theta(1,0));
          fitresult.Fill(g, mc_templates[i]*Theta(0,0) + mc_templates[i+1]*Theta(1,0));

        for i in range(0,len(data)):
       
          data_hist.Fill(i,data[i])
          if isdata == "MC": data_hist.SetBinError(i+1,data_err[i])
          if isdata == "Data": data_hist.SetBinError(i+1,self.Poission(data_hist.GetBinContent(i+1)))
        
        chi2pre = self.Chi2(data_hist,fitresult,num_param,2)

        Dict[jet_mult][suffix]["Theta"] = [ Theta(0,0),Theta(1,0)]
        Dict[jet_mult][suffix]["Chi_2"] = chi2pre[0]
        Dict[jet_mult][suffix]["ndof"] = chi2pre[1]

        print "Chi squared value for Fit to %s is : %s" %(isdata,chi2pre[0])

        self.c1.cd(1)
        fitresult.GetYaxis().SetTitle("Events");
        fitresult.GetXaxis().SetTitle("Num B-tags")
        fitresult.SetTitle("Template fit to %s , Num Jets = %s" %(isdata,jet_mult))
        fitresult.SetLineColor(kBlack)
        fitresult.SetLineWidth(3)
        fitresult.Draw("l")
        template2.SetLineColor(kBlue)
        template2.SetLineWidth(2)
        template2.Draw("samel")
        template0.SetLineColor(kRed)
        template0.SetLineWidth(2)
        template0.Draw("samel")
        data_hist.SetMarkerStyle(20)
        data_hist.Draw("samepe1x0")
        self.TextBox(chi2pre[0],chi2pre[1],label="Pre")
        #self.c1.SaveAs("SimFit_To_%s_%s_%s_HTbin_%s_jet_mult_%s_num_param_%s.png"%(isdata,suffix,self.Working_Point,self.current_htbin,(jet_mult if combine != "True" else "Simultaneous"),num_param))
        
     def TextBox(self,chi_value,ndof,label=""):
        Textbox = TLatex()
        Textbox.SetNDC()
        Textbox.SetTextAlign(12)
        Textbox.SetTextSize(0.04)
        if label == "Pre": Textbox.DrawLatex(0.45,0.85, "Chi^2 Parameters in fit : %4.3f, ndof: %s "  %(chi_value,ndof))
        if label == "Post": Textbox.DrawLatex(0.45,0.80, "Chi^2 Signal Region : %4.3f, ndof: %s" %(chi_value,ndof))

        
     def Chi2(self,data_hist,fit_hist,ndof,constraints,label=''):

             chi_sum = 0
             for i in range(0,data_hist.GetNbinsX()):
                if data_hist.GetBinError(i+1) != 0 and label == "Post" and i > 2:
                        chi_sum += (pow((data_hist.GetBinContent(i+1)-fit_hist.GetBinContent(i+1)),2)/pow(data_hist.GetBinError(i+1),2))
                        #print "Data: %s Fit: %s Data Error: %s ChiSum : %s"%(data_hist.GetBinContent(i+1),fit_hist.GetBinContent(i+1),data_hist.GetBinError(i+1),chi_sum)
                if data_hist.GetBinError(i+1) != 0 and i < (ndof) and label != "Post":
                        chi_sum += (pow((data_hist.GetBinContent(i+1)-fit_hist.GetBinContent(i+1)),2)/pow(data_hist.GetBinError(i+1),2))
                        #print "Data: %s Fit: %s Data Error: %s ChiSum : %s"%(data_hist.GetBinContent(i+1),fit_hist.GetBinContent(i+1),data_hist.GetBinError(i+1),chi_sum)

             ndof = (ndof-constraints)
             chi_sum =chi_sum/ndof

             return chi_sum,ndof

     def Poission(self,value):

        eh =  [1.15, 1.36, 1.53, 1.73, 1.98, 2.21, 2.42, 2.61, 2.80, 3.00 ]
        el =  [0.00, 1.00, 2.00, 2.14, 2.30, 2.49, 2.68, 2.86, 3.03, 3.19 ]
            
        if float(value) < 10: error =  eh[int(value)]
        else: error = sqrt(value)

        return error

     def Extract_Data(self,sample_list,htbin,jet_mult,Dict,isdata):
           
          file = r.TFile.Open("%s.root" %sample_list[0])
          data_array = []
          data_array_err = []        
 
          if sample_list[3] == "Had": pathtobtagdist = sample_list[1]+htbin+"/Jad_Btag_Post_AlphaT_5_55_%s_%s"%(self.Working_Point,jet_mult)
          else:  pathtobtagdist = sample_list[1]+htbin+"/Jad_Btag_Pre_AlphaT_5_%s_%s"%(self.Working_Point,jet_mult)

          btagdist = file.Get(pathtobtagdist)
          for i in range(0,btagdist.GetNbinsX()):
              data_array.append(btagdist.GetBinContent(i+1))
              if isdata == "Data": data_array_err.append(self.Poission((btagdist.GetBinContent(i+1))))
              else: data_array_err.append(btagdist.GetBinError(i+1))

          Dict[jet_mult]["Data"] = data_array
          Dict[jet_mult]["Data_Err"] = data_array_err
          Dict[jet_mult]["Data_Err_Matrix"] = [0.0]*int(pow(len(data_array[:self.fitparam]),2))
          
          for i in range(0,len(data_array[:self.fitparam])):
                for j in range(0,len(data_array[:self.fitparam])):
                    counter = (i*len(data_array[:self.fitparam]))+j
                    if (i== j):Dict[jet_mult]["Data_Err_Matrix"][counter] =(pow(data_array_err[i],2))

     def Btag_Rate(self,sample_list,htbin,jet_mult,MC_Dict,isdata):

          pass_var = sample_list[2]
          
          file = r.TFile.Open("%s.root" %sample_list[0])
          DirKeys = file.GetListOfKeys()
          for entry in DirKeys:
             subdirect = file.FindObjectAny(entry.GetName())
             dir = sample_list[1]+htbin
             subdirect.GetName()
             if dir == subdirect.GetName():
              for entry in ["","_plus","_minus"]:
               
                sflightsuffix = ""
                sfbsuffix = ""
                if isdata == "Data":
                  sflightsuffix = "SFlight"+entry+"_"
                  sfbsuffix = "SFb"+entry+"_"

                for subkey in [ "GenJetPt_nBgen_"+jet_mult, "GenJetPt_noB_nBgen_"+jet_mult, "GenJetPt_c_nBgen_"+jet_mult, "Btagged_GenJetPt_nBgen_"+sfbsuffix+self.Working_Point+"_"+jet_mult, "Btagged_GenJetPt_noB_nBgen_"+sflightsuffix+self.Working_Point+"_"+jet_mult, "Btagged_GenJetPt_c_nBgen_" +sflightsuffix+self.Working_Point+"_"+jet_mult  ]:

                 #========================================#
                   if subkey  == "GenJetPt_noB_nBgen_%s"%jet_mult:

                       mistag_plot = file.Get(dir+"/"+subkey)
                       err = r.Double(0.0)
                       MC_Dict[jet_mult][pass_var]['Mistag_Efficiency%s'%entry] =mistag_plot.Integral()
                       mistag_plot.IntegralAndError(1,10000,err)
                       
                       if entry == "":
                         try: MC_Dict[jet_mult][pass_var]["Mistag_Error"] = err/mistag_plot.Integral()
                         except ZeroDivisionError: MC_Dict[jet_mult][pass_var]["Mistag_Error"] = 0.0
                       
                   if isdata == "Data": mistagname = "Btagged_GenJetPt_noB_nBgen_SFlight%s_%s_%s"%(entry,self.Working_Point,jet_mult)
                   if isdata == "MC": mistagname = "Btagged_GenJetPt_noB_nBgen_%s_%s"%(self.Working_Point,jet_mult)
                   
                   if subkey == mistagname:
                       
                       mplot = file.Get(dir+"/"+subkey)
                       err = r.Double(0.0)
                       try :MC_Dict[jet_mult][pass_var]['Mistag_Efficiency%s'%entry] = mplot.Integral()/(MC_Dict[jet_mult][pass_var]['Mistag_Efficiency%s'%entry])
                       except ZeroDivisionError: MC_Dict[jet_mult][pass_var]['Mistag_Efficiency%s'%entry] = 0.0
                       mplot.IntegralAndError(1,10000,err)
                       
                       if entry == "":
                         try: MC_Dict[jet_mult][pass_var]["Mistag_Error"] =  MC_Dict[jet_mult][pass_var]['Mistag_Efficiency']*sqrt(pow(MC_Dict[jet_mult][pass_var]["Mistag_Error"],2)+pow(err/mplot.Integral(),2))
                         except ZeroDivisionError: MC_Dict[jet_mult][pass_var]["Mistag_Error"] = 0.0

                   #========================================#
                   if subkey == "GenJetPt_c_nBgen_%s"%jet_mult:

                       ctag_plot = file.Get(dir+"/"+subkey)
                       err = r.Double(0.0)
                       MC_Dict[jet_mult][pass_var]['Ctag_Efficiency%s'%entry] =ctag_plot.Integral()
                       ctag_plot.IntegralAndError(1,10000,err)
                       
                       if entry == "":
                         try: MC_Dict[jet_mult][pass_var]["Ctag_Error"] = err/ctag_plot.Integral()
                         except ZeroDivisionError: MC_Dict[jet_mult][pass_var]["Ctag_Error"] = 0.0

                   if isdata == "Data": ctagname = "Btagged_GenJetPt_c_nBgen_SFlight%s_%s_%s"%(entry,self.Working_Point,jet_mult)
                   if isdata == "MC": ctagname = "Btagged_GenJetPt_c_nBgen_%s_%s"%(self.Working_Point,jet_mult)
                  
                   if subkey == ctagname:
                       
                       cplot = file.Get(dir+"/"+subkey)
                       err = r.Double(0.0)
                       try :MC_Dict[jet_mult][pass_var]['Ctag_Efficiency%s'%entry] = cplot.Integral()/(MC_Dict[jet_mult][pass_var]['Ctag_Efficiency%s'%entry])
                       except ZeroDivisionError: MC_Dict[jet_mult][pass_var]['Ctag_Efficiency%s'%entry] = 0.0
                       cplot.IntegralAndError(1,10000,err)
                       
                       if entry == "":
                         try: MC_Dict[jet_mult][pass_var]["Ctag_Error"] =  MC_Dict[jet_mult][pass_var]['Ctag_Efficiency']*sqrt(pow(MC_Dict[jet_mult][pass_var]["Ctag_Error"],2)+pow(err/cplot.Integral(),2))
                         except ZeroDivisionError: MC_Dict[jet_mult][pass_var]["Ctag_Error"] = 0.0

                  #============================

                   if subkey == "GenJetPt_nBgen_%s"%jet_mult:

                       err = r.Double(0.0)     
                       btag_gen_plot = file.Get(dir+"/"+subkey)
                       btag_gen_plot.IntegralAndError(1,10000,err)
                       MC_Dict[jet_mult][pass_var]["Btag_Efficiency%s"%entry] = btag_gen_plot.Integral()
                       if entry == "":
                         try:MC_Dict[jet_mult][pass_var]["Btag_Error"] = err/btag_gen_plot.Integral()
                         except ZeroDivisionError : MC_Dict[jet_mult][pass_var]["Btag_Error"] = 0.0

                   if isdata == "Data": btagname = "Btagged_GenJetPt_nBgen_SFb%s_%s_%s"%(entry,self.Working_Point,jet_mult)
                   if isdata == "MC": btagname = "Btagged_GenJetPt_nBgen_%s_%s"%(self.Working_Point,jet_mult)

                   if subkey  == btagname:

                       err = r.Double(0.0)
                       bplot = file.Get(dir+"/"+subkey)
                       bplot.IntegralAndError(1,10000,err)
                       
                       try: MC_Dict[jet_mult][pass_var]['Btag_Efficiency%s'%entry] = bplot.Integral()/(MC_Dict[jet_mult][pass_var]['Btag_Efficiency%s'%entry])
                       except ZeroDivisionError: MC_Dict[jet_mult][pass_var]['Btag_Efficiency%s'%entry] = 0.0

                       if entry == "":
                          try: MC_Dict[jet_mult][pass_var]["Btag_Error"] =  MC_Dict[jet_mult][pass_var]['Btag_Efficiency']*sqrt(pow(MC_Dict[jet_mult][pass_var]["Btag_Error"],2)+pow(err/bplot.Integral(),2))
                          except ZeroDivisionError: MC_Dict[jet_mult][pass_var]["Btag_Error"] = 0.0

          file.Close()
            
     def Generate_Templates(self,sample,htbin,jet_mult,Dict,isdata):

          file = r.TFile.Open("%s.root" %sample[0])

          if sample[3] == "Had": pathtomatched = sample[1]+htbin+"/Matched_vs_Matched_Template_noB_vs_c_alphaT_%s"%jet_mult  
          else: pathtomatched = sample[1]+htbin+"/Matched_vs_Matched_Template_noB_vs_c_%s"%jet_mult

          variable = sample[2]

          s_vs_b = file.Get(pathtomatched)
          
          comparedict = {'Normal':'','Plus':"_plus",'Minus':"_minus"}
          for suffix in comparedict:
            Formula_List = self.Yield_Calculator(s_vs_b,jet_mult,variable,Dict,comparedict[suffix],isdata)
            if isdata == "Data":
                for num,i in enumerate(Formula_List[0]):
                     Formula_List[0][num] = i* float(self.Lumo) * 10
                     Formula_List[1][num] = Formula_List[1][num]* float(self.Lumo) * 10

            Dict[jet_mult][suffix]["Full_Template"].append(Formula_List[0])
          file.Close()

     def Yield_Calculator(self,s_vs_b,jet_mult,hypothesis_category,Dict,suffix,isdata):
          
          def bcombo(b, s,charm, e, m,c,  hist):

              Nb = b;
              Ns = s;
              Nc = charm;

              #here you set the upper limits for the loop...
              Nbmax = 4 #hist.GetNbinsX()
              Nsmax = hist.GetNbinsY()
              Ncmax =  4 #hist.GetNbinsZ()

              #this is the result to return...
              final_yield = 0.0
              final_error = 0.0
              for x in range(Nb,Nbmax):
                for y in range(Ns,Nsmax):
                  for z in range(Nc,Ncmax):

                    final_yield += hist.GetBinContent(x+1, y+1,z+1) * TMath.Binomial(x,b) * pow(e,b) * pow(1.0 - e, x-b) * TMath.Binomial(y,s) * pow(m,s) * pow(1.0 - m, y-s) * TMath.Binomial(z,charm) * pow(c,charm) * pow(1.0 - c, z-charm)

                    final_error += pow(hist.GetBinError(x+1, y+1,z+1) * TMath.Binomial(x,b) * pow(e,b) * pow(1.0 - e, x-b) * TMath.Binomial(y,s) * pow(m,s) * pow(1.0 - m, y-s) * TMath.Binomial(z,charm) * pow(c,charm) * pow(1.0 - c, z-charm) ,2)
 
              return(final_yield,final_error)
                
          Yields = []
          Yields_Error = []
          Formula_List = [0,1,2,3,4]
          
          if isdata == "MC":
                if suffix == "_plus":
                        
                        new_eff =  Dict[jet_mult][hypothesis_category]["Btag_Efficiency"] +   Dict[jet_mult][hypothesis_category]["Btag_Error"]      
                        new_mis  = Dict[jet_mult][hypothesis_category]["Mistag_Efficiency"] + Dict[jet_mult][hypothesis_category]["Mistag_Error"]
                        new_ceff  = Dict[jet_mult][hypothesis_category]["Ctag_Efficiency"] + Dict[jet_mult][hypothesis_category]["Ctag_Error"]
                        
                        
                if suffix == "_minus":
                        
                        new_eff =  Dict[jet_mult][hypothesis_category]["Btag_Efficiency"] -   Dict[jet_mult][hypothesis_category]["Btag_Error"]      
                        new_mis  = Dict[jet_mult][hypothesis_category]["Mistag_Efficiency"] - Dict[jet_mult][hypothesis_category]["Mistag_Error"]
                        new_ceff  = Dict[jet_mult][hypothesis_category]["Ctag_Efficiency"] - Dict[jet_mult][hypothesis_category]["Ctag_Error"]

                        
                if suffix == "":
                        
                        new_eff =  Dict[jet_mult][hypothesis_category]["Btag_Efficiency"]       
                        new_mis  = Dict[jet_mult][hypothesis_category]["Mistag_Efficiency"] 
                        new_ceff  = Dict[jet_mult][hypothesis_category]["Ctag_Efficiency"] 
          else: 

                new_eff =  Dict[jet_mult][hypothesis_category]["Btag_Efficiency"]       
                new_mis  = Dict[jet_mult][hypothesis_category]["Mistag_Efficiency"] 
                new_ceff  = Dict[jet_mult][hypothesis_category]["Ctag_Efficiency"] 

          for num in Formula_List:
                
             if float(num) <= float(jet_mult):
                temp_yield = 0.0
                temp_yield_error = 0.0
                for j in range(0,num+1):
                  for k in range(0,num+1):
                    for l in range (0,num+1):
                      if j + k + l == num:
                          temp_yield += bcombo(j,k,l,new_eff,new_mis,new_ceff,s_vs_b)[0]
                          temp_yield_error += bcombo(j,k,l,new_eff,new_mis,new_ceff,s_vs_b)[1]

                Yields.append(temp_yield)
                Yields_Error.append(sqrt(temp_yield_error))

          return (Yields,Yields_Error)


