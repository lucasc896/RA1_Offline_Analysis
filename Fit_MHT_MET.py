#!/usr/bin/env python
from ROOT import *
import ROOT as r
import logging,itertools
import os,fnmatch,sys

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
r.gStyle.SetOptFit(1)

"""
Take Data/MC Ratio from running Prediction_RA1 -m . which gives total data/MC ratio for each pure sample

0-btag 2,3 jets,muon selection - WJets
0-btag 2,3jet, dimuon selection - DY
2-btag >=4 jet , muon selection - TTbar

They are they just input into the lists below by hand.
With a bit of effort this can be automated in NumberCruncher to fill automatically produce these fits from the lists given by writing a little function. 
I just haven't got around to it yet.

"""


# Mean ht bins of each bin in analysis 1300 is just used to define end of histogram x-axis.
#htbin = [178.2,235.2,297.5,347.5,416.4,517.3,618.4,716.9,819.9,919.,1019.,1289.,1300.]
htbin = [235.2,297.5,347.5,416.4,517.3,618.4,716.9,819.9,919.,1019.,1289.,1300.]

# Start fit from fitstart and go on for fitlength.
fitnum = 11
fitlength = 11
fitstart = 0

# bands for PU ISR Parton Reweight
"""

#WJets
signal_list_zero = [0.89,0.86,0.85,0.81,0.83,0.81,0.85,0.77,0.78,0.78,0.93,0.90]
signal_list_zero_err = [0.01,0.01,0.01,0.01,0.01,0.02,0.03,0.04,0.05,0.07,0.11,0.90]

sideband_list_zero = [0.91,0.88,0.84,0.89,0.86,0.88,0.80,0.79,0.95,0.73,0.75,0.74]
sideband_list_zero_err = [0.02,0.01,0.02,0.02,0.02,0.03,0.05,0.07,0.11,0.14,0.18,0.15]

#TTbar
signal_list_two = [0.,1.05,1.05,1.03,0.91,0.95,0.90,1.00,0.78,0.66,0.43,0.53]
signal_list_two_err = [0.0,0.06,0.03,0.04,0.04,0.05,0.06,0.10,0.12,0.15,0.18,0.18]

sideband_list_two = [0.0,1.01,1.04,0.88,1.05,0.91,0.81,0.81,0.97,0.7,0.70,0.54]
sideband_list_two_err = [0.0,0.08,0.04,0.05,0.06,0.07,0.09,0.14,0.27,0.48,0.47,0.42]

#DY, Photon also used correction derived from here.
dimuon_list_zero = [0.91,0.90,0.94,0.94,0.92,0.80,0.97,0.78,0.90,0.79,1.03,0.68]
dimuon_list_zero_err = [0.03,0.02,0.02,0.03,0.03,0.04,0.07,0.09,0.14,0.18,0.29,0.19]

dimuon_sideband_list_zero = [0.87,0.84,0.89,0.91,0.80,0.82,0.79,1.06,0.82,0.56,0.35,1.75]
dimuon_sideband_list_zero_err = [0.05,0.03,0.04,0.06,0.06,0.09,0.14,0.25,0.29,0.32,0.48,0.62]


# bands for PU ISR Using Table yields with error propagation
#TTbar
signal_list_two = [0.0,1.05,1.05,1.03,0.91,0.95,0.90,1.00,0.77,0.66,0.43,0.53]
signal_list_two_err = [0.0,0.06,0.03,0.04,0.04,0.05,0.06,0.10,0.12,0.15,0.18,0.18]

sideband_list_two = [0.0,1.01,1.04,0.88,1.05,0.91,0.81,0.81,0.97,0.7,0.70,0.54,]
sideband_list_two_err = [0.0,0.08,0.04,0.05,0.06,0.07,0.09,0.14,0.27,0.48,0.47,0.42]

#DY
dimuon_list_zero = [0.96,0.95,0.98,0.96,0.90,0.75,0.89,0.69,0.77,0.65,0.82,0.48]
dimuon_list_zero_err = [0.03,0.02,0.02,0.03,0.03,0.04,0.06,0.08,0.12,0.15,0.23,0.14]

dimuon_sideband_list_zero = [0.92,0.89,0.93,0.93,0.78,0.77,0.72,0.93,0.70,0.46,0.28,1.22]
dimuon_sideband_list_zero_err = [0.05,0.03,0.04,0.06,0.05,0.09,0.13,0.22,0.25,0.27,0.38,0.43]

#WJets
signal_list_zero = [0.92,0.89,0.85,0.81,0.81,0.78,0.79,0.69,0.68,0.65,0.75,0.66]
signal_list_zero_err = [0.01,0.01,0.01,0.01,0.01,0.02,0.02,0.03,0.04,0.06,0.09,0.07]

sideband_list_zero = [0.95,0.91,0.85,0.89,0.85,0.84,0.74,0.70,0.82,0.61,0.60,0.54]
sideband_list_zero_err = [0.02,0.01,0.02,0.02,0.02,0.03,0.04,0.06,0.10,0.11,0.14,0.11]
"""

#TTbar
signal_list_two = [1.06,1.05,1.04,0.97,1.0,0.93,0.97,0.74,0.79,0.21,0.97]
signal_list_two_err = [0.06,0.03,0.04,0.04,0.05,0.06,0.10,0.12,0.18,0.15,0.25]

sideband_list_two = [0.98,1.07,0.88,0.92,0.83,0.88,0.59,0.95,1.50,0.21,0.71]
sideband_list_two_err = [0.07,0.04,0.05,0.06,0.06,0.10,0.13,0.24,0.44,0.32,0.44]

#DY
dimuon_list_zero = [1.13,0.97,0.93,0.89,0.81,0.84,0.76,0.68,0.69,0.69,0.48,1.01]
dimuon_list_zero_err = [0.02,0.02,0.03,0.03,0.04,0.06,0.08,0.11,0.15,0.21,0.13]

dimuon_sideband_list_zero = [1.05,0.93,0.83,0.81,0.82,0.71,0.66,0.62,0.45,0.27,0.94]
dimuon_sideband_list_zero_err = [0.03,0.04,0.05,0.06,0.09,0.13,0.18,0.24,0.26,0.37,0.39]

#WJets
signal_list_zero = [0.89,0.86,0.82,0.80,0.78,0.81,0.67,0.68,0.60,0.68,0.56,0.86]
signal_list_zero_err = [0.01,0.01,0.01,0.01,0.02,0.02,0.03,0.04,0.06,0.08,0.06,0.01]

sideband_list_zero = [0.89,0.82,0.83,0.80,0.80,0.68,0.69,0.72,0.63,0.65,0.45]
sideband_list_zero_err = [0.01,0.02,0.02,0.02,0.03,0.04,0.06,0.09,0.11,0.15,0.10]






signal = r.TGraphErrors(12)
side = r.TGraphErrors(12)

signal_ttbar = r.TGraphErrors(12)
side_ttbar = r.TGraphErrors(12)

signal_dimuon = r.TGraphErrors(12)
side_dimuon = r.TGraphErrors(12)

signal.SetLineColor(4)
signal_ttbar.SetLineColor(4)
signal_dimuon.SetLineColor(4)

for n,entry in enumerate(signal_list_two):

     signal.SetPoint(n+1,htbin[n],signal_list_zero[n])
     signal.SetPointError(n+1,0,signal_list_zero_err[n])

     side.SetPoint(n+1,htbin[n],sideband_list_zero[n])
     side.SetPointError(n+1,0,sideband_list_zero_err[n])

     signal_ttbar.SetPoint(n+1,htbin[n],signal_list_two[n])
     signal_ttbar.SetPointError(n+1,0,signal_list_two_err[n])

     side_ttbar.SetPoint(n+1,htbin[n],sideband_list_two[n])
     side_ttbar.SetPointError(n+1,0,sideband_list_two_err[n])

     signal_dimuon.SetPoint(n+1,htbin[n],dimuon_list_zero[n])
     signal_dimuon.SetPointError(n+1,0,dimuon_list_zero_err[n])

     side_dimuon.SetPoint(n+1,htbin[n],dimuon_sideband_list_zero[n])
     side_dimuon.SetPointError(n+1,0,dimuon_sideband_list_zero_err[n])


signal.GetYaxis().SetRangeUser(0.0,1.9)
signal.GetXaxis().SetRangeUser(150,1500)

signal.Draw("AP")

fit_signal = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
signal.Fit(fit_signal,"R")
fit_signal.SetLineColor(4)
fit_signal.Draw("SAME")

c1.SaveAs("./signal_zero_wjets.png")

side.GetYaxis().SetRangeUser(0.0,1.9)
side.GetXaxis().SetRangeUser(150,1500)

side.Draw("AP")

fit_side = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
side.Fit(fit_side,"R")


fit_side.Draw("SAME")
#signal.Draw("SAMEP")
#fit_signal.Draw("SAME")

c1.SaveAs("./sideband_zero_wjets.png")

signal_dimuon.GetYaxis().SetRangeUser(0.0,1.9)
signal_dimuon.GetXaxis().SetRangeUser(150,1500)

signal_dimuon.Draw("AP")

fit_signal_dimuon = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
signal_dimuon.Fit(fit_signal_dimuon,"R")
fit_signal_dimuon.SetLineColor(4)
fit_signal_dimuon.Draw("SAME")

c1.SaveAs("./signal_zero_dimuon.png")

side_dimuon.GetYaxis().SetRangeUser(0.0,1.9)
side_dimuon.GetXaxis().SetRangeUser(150,1500)

side_dimuon.Draw("AP")

fit_side_dimuon = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
side_dimuon.Fit(fit_side_dimuon,"R")

#signal_dimuon.Draw("SAMEP")
#fit_signal_dimuon.Draw("SAME")
fit_side_dimuon.Draw("SAME")

c1.SaveAs("./sideband_zero_dimuon.png")

signal_ttbar.GetXaxis().SetRangeUser(150,1500)
signal_ttbar.GetYaxis().SetRangeUser(0.0,1.9)

signal_ttbar.Draw("AP")

fit_signal_ttbar = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
signal_ttbar.Fit(fit_signal_ttbar,"R")
fit_signal_ttbar.SetLineColor(4)
fit_signal_ttbar.Draw("SAME")

c1.SaveAs("./signal_two_ttbar.png")


side_ttbar.GetXaxis().SetRangeUser(150,1500)
side_ttbar.GetYaxis().SetRangeUser(0.0,1.9)
side_ttbar.Draw("AP")

fit_side_ttbar = r.TF1("fit","pol1", htbin[fitstart]-50, htbin[fitlength])
side_ttbar.Fit(fit_side_ttbar,"R")

fit_side_ttbar.Draw("SAME")
#signal_ttbar.Draw("SAMEP")
#fit_signal_ttbar.Draw("SAME")

c1.SaveAs("./sideband_two_ttbar.png")

