#!/usr/bin/env python
from ROOT import *
import ROOT as r
import numpy as np

c1= r.TCanvas("Yields", "Yields",0,0,900,600)
c1.SetHighLightColor(2)
c1.SetFillColor(0)
c1.SetBorderMode(0)
c1.SetBorderSize(2)
c1.SetTickx(1)
c1.SetTicky(1)
c1.SetFrameBorderMode(0)
c1.SetFrameBorderMode(0)
c1.cd(1)

def MakeConfidencePlot(yval,yerr,name,col):

        graph = r.TGraphErrors(int(fitnum),
                               np.array(htbin),
                               np.array(yval),
                               np.array(htbinerr),
                               np.array(yerr))
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.5)

        graph.GetYaxis().SetRangeUser(0.0,1.3)
        graph.GetXaxis().SetRangeUser(150,1500)
        graph.SetTitle(name)
        graph.Draw("pa")

        fit = r.TF1("pol1","pol1",htbin[fitstart]-50, htbin[fitlength] )
        fit.SetLineColor(col)
        result = graph.Fit("pol1","RS");

        xx = np.array(fullhtbins)
        yy = np.array([float(fit.Eval(x)) for x in xx])
        ee = np.array([0.]*len(xx))

        result.GetConfidenceIntervals(len(xx),1,1,xx,ee,0.683,False)
        conf = r.TGraphErrors(len(xx)-1,
                              np.array(xx),
                              np.array(yy),
                              np.array([0.]*len(xx)),
                              np.array(ee))
        conf.SetFillStyle(3001)
        conf.SetFillColor(col)
        conf.Draw("3same")
        c1.SaveAs("./"+name+".png")

        if "Sideband" in name: 
             print "Appending to dictionary %s" %name
             process = name.split('_')[0]
             for bin in bin_edge:
                current_index = fullhtbins.index(meanbin_dict[str(bin)])
                correction_dict[bin][process]["Correction"] = yy[current_index]
                correction_dict[bin][process]["Error"] = ee[current_index]


fitnum = 11
fitlength = 11
fitstart = 0

correction_dict = { }
bin_edge = ["150","200","275","325","375","475","575","675","775","875","975","1075"]
fullhtbins = [178.2,235.2,297.5,347.5,416.4,517.3,618.4,716.9,819.9,919.,1019.,1289.,1300.]
meanbin_dict = {"150":178.2,"200":235.2,"275":297.5,"325":347.5,"375":416.4,"475":517.3,"575":618.4,"675":716.9,"775":819.9,"875":919.,"975":1019.,"1075":1289.}
process = ('WJets','TTbar','DY')
entries = ('Correction','Error')

correction_dict = dict.fromkeys(bin_edge)  

for key in bin_edge:
  correction_dict[key] = dict.fromkeys(process) 
  for SM in process :
     correction_dict[key][SM] = dict.fromkeys(entries,0)

htbin = [235.2,297.5,347.5,416.4,517.3,618.4,716.9,819.9,919.,1019.,1289.,1300.]
htbinerr = [0.]*len(htbin)

#WJets
wjet_sig = [0.89,0.86,0.82,0.80,0.78,0.81,0.67,0.68,0.60,0.68,0.56,0.86]
wjet_sig_err = [0.01,0.01,0.01,0.01,0.02,0.02,0.03,0.04,0.06,0.08,0.06,0.01]

wjet_side = [0.89,0.82,0.83,0.80,0.80,0.68,0.69,0.72,0.63,0.65,0.45]
wjet_side_err = [0.01,0.02,0.02,0.02,0.03,0.04,0.06,0.09,0.11,0.15,0.10]

#DY
dy_sig = [0.95,0.96,0.93,0.89,0.81,0.84,0.76,0.68,0.69,0.69,0.48,1.01]
dy_sig_err = [0.02,0.02,0.03,0.03,0.04,0.06,0.08,0.11,0.15,0.21,0.13]

dy_side = [0.86,0.92,0.83,0.80,0.82,0.71,0.66,0.62,0.45,0.27,0.94]
dy_side_err = [0.03,0.04,0.05,0.06,0.09,0.13,0.18,0.24,0.26,0.37,0.39]

#TTbar  = gr1 btags
ttbar_sig = [1.15,1.08,1.03,0.97,0.99,0.88,0.93,0.76,0.67,0.11,0.85]
ttbar_sig_err = [0.02,0.02,0.03,0.03,0.04,0.05,0.08,0.11,0.14,0.11,0.21]

ttbar_side = [1.09,1.04,0.88,0.92,0.84,0.92,0.69,1.02,1.716,0.14,0.68]
ttbar_side_err = [0.073,0.03,0.04,0.04,0.05,0.09,0.12,0.21,0.43,0.25,0.37]


MakeConfidencePlot(wjet_sig,wjet_sig_err,"WJets_Signal",2)
MakeConfidencePlot(wjet_side,wjet_side_err,"WJets_Sideband",4)

MakeConfidencePlot(dy_sig,dy_sig_err,"DY_Signal",2)
MakeConfidencePlot(dy_side,dy_side_err,"DY_Sideband",4)

MakeConfidencePlot(ttbar_sig,ttbar_sig_err,"TTbar_Signal",2)
MakeConfidencePlot(ttbar_side,ttbar_side_err,"TTbar_Sideband",4)

print correction_dict
