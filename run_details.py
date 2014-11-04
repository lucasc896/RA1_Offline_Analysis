
def this_run():

	selector = "03Nov_alphaT0p6_0p7_v0"

	out_dict = {}

	out_dict["07Dec_SITV"] = {
		"path_name": "rootfiles/Root_Files_07Dec_Full2013_Parked_noISRRW_SITV_fixedCode",
		
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,
		
		"wj_corr": 0.9, # note: 0.85 gives a better post-correction agreement
		"dy_corr": 3.02,
		"tt_corr": 1.2,
	}

	out_dict["10Dec_AlphaT0p6"] = {
		"path_name": "rootfiles/test_space",
		
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,
		
		"wj_corr": 0.92,
		"dy_corr": 0.96,
		"tt_corr": 1.23,
	}	

	out_dict["05Dec_v2_GOLDEN"] = {
		"path_name": "rootfiles/GOLDEN",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# "wj_corr": 0.92,
		# "dy_corr": 0.96,
		"tt_corr": 1.23,

		# # Run A
		# "had_lumi": 0.,
		# "mu_lumi": .685538,
		# "ph_lumi": .682937,


		# "wj_corr": 0.94,
		# "dy_corr": 1.06,
		# "tt_corr": 1.63,

		# # Run B
		# "had_lumi": 4.412,
		# "mu_lumi": 4.402,
		# "ph_lumi": 4.402,


		# "wj_corr": 0.92,
		# "dy_corr": 0.91,
		# "tt_corr": 1.13,

		# # Run C
		# "had_lumi": 6.795,
		# "mu_lumi": 6.770,
		# "ph_lumi": 6.768,


		# "wj_corr": 0.93,
		# "dy_corr": 0.99,
		# "tt_corr": 1.31,

		# # Runs D
		# "had_lumi": 7.287,
		# "mu_lumi": 7.273,
		# "ph_lumi": 7.267,

		# "wj_corr": 0.91,
		# "dy_corr": 0.94,
		# "tt_corr": 1.19,

		# # Run ABC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.8575,
		# "ph_lumi": 11.8529,

		# "wj_corr": 0.93,
		# "dy_corr": 0.97,
		# "tt_corr": 1.26,

		# # Run BC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.172,
		# "ph_lumi": 11.17,

		# "wj_corr": 0.93,
		# "dy_corr": 0.96,
		# "tt_corr": 1.24,

	}

	# a.k.a. the "19Dec" website files
	out_dict["18Dec_CorrFactors"] = {
		"path_name": "rootfiles/Root_Files_17Dec_Full2013_noISRRW_noSITV_fixedXS_fixedCode",
		
		# All Runs
		# with corrections
		# "had_lumi": 18.493,
		# "mu_lumi": 19.131,
		# "ph_lumi": 19.12,

		# "wj_corr": 0.92,
		# "dy_corr": 0.97,
		# "tt_corr": 1.22,

		# HCP values
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# pre trigger update
		# "wj_corr": 0.92,
		# "dy_corr": 0.97,
		# "tt_corr": 1.22,

		# post trigger update
		"wj_corr": 0.91,
		"dy_corr": 0.94,
		"tt_corr": 1.21, #1.27 from Pure TTbar ratio

	}

	out_dict["25Jan_ISRRW_Test"] = {
		"path_name": "rootfiles/Root_Files_25Jan_Full2013_ISRRW_noSITV_fixedXS_fixedCode",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		"wj_corr": 0.92,
		"dy_corr": 0.96,
		"tt_corr": 1.23,


	}


	out_dict["28Jan_globalAlphaT"] = {

		"path_name": "rootfiles/Root_Files_28Jan_Full2013_noISRRW_noSITV_fixedXS_globalAlphaT_fixedCode",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# "wj_corr": 1.01,
		# "dy_corr": 0.54,
		# "tt_corr": 1.30,

		"wj_corr": 0.92,
		"dy_corr": 0.97,
		"tt_corr": 1.22,


	}

	out_dict["28Jan_globalAlphaT_v3"] = {

		"path_name": "rootfiles/Root_Files_28Jan_Full2013_noISRRW_noSITV_fixedXS_globalAlphaT_fixedCode_v3",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrections, with alphaT in muon
		"wj_corr": 0.91,
		"dy_corr": 0.98,
		"tt_corr": 1.26,

		# old corrections, no alphaT in muon
		# "wj_corr": 0.92,
		# "dy_corr": 0.97,
		# "tt_corr": 1.22,

	}

	out_dict["10Feb_30SecondMu_v1"] = {

		"path_name": "rootfiles/Root_Files_10Feb_Full2013_noISRRW_noSITV_fixedXS_30SecondMu",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# note: corrections for ttbar use le3j now
		"wj_corr": 0.91,
		"dy_corr": 0.95,
		"tt_corr": 1.19, # taken from the overall data/MC ratio
		# "tt_corr": 1.19, # taken from the pure ttbar ratio

	}

	out_dict["11Feb_30SecondMu_NewZMassCut"] = {

		"path_name": "rootfiles/Root_Files_11Feb_Full2013_noISRRW_noSITV_fixedXS_30SecondMu_NewZMassCut",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}


	out_dict["13Feb_30SecondMu_NoZMassCutSingleMu"] = {

		"path_name": "rootfiles/Root_Files_13Feb_Full2013_noISRRW_noSITV_fixedXS_30SecondMu_noZMassCutInSingleMu",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}
	

	out_dict["19Feb_30SecondMu_NoZMassCutSingleMu_30Global"] = {

		"path_name": "rootfiles/Root_Files_19Feb_Full2013_noISRRW_noSITV_fixedXS_30SecondMu_noZMassCutInSingleMu_RaisedCommonMu30_IC",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.97,
		"tt_corr": 1.22,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}

	out_dict["19Feb_30SecondMu_NoZMassCutSingleMu_30Global_SITV"] = {

		"path_name": "rootfiles/Root_Files_19Feb_Full2013_noISRRW_SITV_fixedXS_30SecondMu_noZMassCutInSingleMu_RaisedCommonMu30",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}	

	out_dict["rob_IC_test_0"] = {

		"path_name": "rootfiles/rob_IC_test_v4",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# # new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.22,
		# "tt_corr": 1.29, # taken from pure ttbar ratio

		# old corrs
		# "wj_corr": 0.94,
		# "dy_corr": 0.95,
		# "tt_corr": 1.21,

	}	

	out_dict["03March_30SecondMu_NoZMassCutSingleMu_IC"] = {

		"path_name": "rootfiles/Root_Files_03March_Full2013_noISRRW_noSITV_fixedXS_30SecondMu_noZMassCutInSingleMu_IC_RobsRun",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.22,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}

	

	out_dict["05March_NotSure_Rob"] = {

		"path_name": "rootfiles/Root_Files_05March_Full2013_notSure_IC_Rob",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.18,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}

	out_dict["05March_NotSure_Rob_v2"] = {

		"path_name": "rootfiles/Root_Files_March_Full2013_RobLatest_IC",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.19,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}

	out_dict["05March_NotSure_Rob_ChrisCheck"] = {

		"path_name": "rootfiles/Root_Files_05March_Full2013_notSure_IC_Rob_ChrisHadDataCheck",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.18,
		# "tt_corr": 1.27, # taken from pure ttbar ratio

	}



	out_dict["09April_ParkedFinal_HEAD"] = {

		"path_name": "rootfiles/Root_Files_09April_Full2013_ParkedFinal_HEAD_FROMROB_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}


	out_dict["12April_NoSITVTest_HEAD_v0"] = {

		"path_name": "rootfiles/Root_Files_12April_Full2013_NoSITVTest_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,

	}

	out_dict["07May_NoMHTovMET_HEAD_v0"] = {

		"path_name": "rootfiles/Root_Files_07May_Full2013_NoMHTovMET_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.90,
		"dy_corr": 0.92,
		"tt_corr": 1.11,

	}

	out_dict["07May_NoDeadECAL_HEAD_v0"] = {

		"path_name": "rootfiles/Root_Files_07May_Full2013_NoDeadECAL_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.93,
		"dy_corr": 0.92,
		"tt_corr": 1.20,

	}

	out_dict["07May_NoDeadECAL_HEAD_v1"] = {

		"path_name": "rootfiles/Root_Files_07May_Full2013_NoDeadECAL_HEAD_v1",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["16May_AlphaTInMuon_HEAD_v0"] = {

		"path_name": "rootfiles/Root_Files_16May_Full2013_AlphaTInMuon_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		# "wj_corr": 0.95,
		# "dy_corr": 0.96,
		# "tt_corr": 1.18,

		# "current" head corrs
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["12May_NoBtagRW_HEAD_v0"] = {

		"path_name": "rootfiles/Root_Files_12May_Full2013_NoBtagSF_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["19May_fullCrossCheck_v0"] = {

		"path_name": "rootfiles/Root_Files_19May_Full2013_HEAD_fullCrossCheck_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

		# Rob's
		# "wj_corr": 0.91,
		# "dy_corr": 0.95,
		# "tt_corr": 1.16,

	}

	out_dict["19May_raisedAlphaT_v0"] = {

		"path_name": "rootfiles/Root_Files_19May_Full2013_HEAD_raisedAlphaT_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}


	out_dict["21May_head_v1"] = {

		"path_name": "rootfiles/Root_Files_21May_Full2013_HEAD_v1",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["22May_head_v2"] = {

		"path_name": "rootfiles/Root_Files_22May_Full2013_HEAD_v2",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["22May_noSITV_v0"] = {

		"path_name": "rootfiles/Root_Files_22May_Full2013_noSITV_HEAD_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,

	}

	out_dict["25May_RunBC_v0"] = {

		"path_name": "rootfiles/Root_Files_25May_RunBC_HEAD_v0",
		
		# Runs B+C
		"had_lumi": 11.207,
		"mu_lumi": 11.172,
		"ph_lumi": 11.170,

		# new corrs from this set of files
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.14,

	}

	out_dict["25May_RunBC_noSITV_v0"] = {

		"path_name": "rootfiles/Root_Files_25May_RunBC_noSITV_HEAD_v0",
		
		# Runs B+C
		"had_lumi": 11.207,
		"mu_lumi": 11.172,
		"ph_lumi": 11.170,

		# new corrs from this set of files
		"wj_corr": 0.94,
		"dy_corr": 0.95,
		"tt_corr": 1.21,

	}

	out_dict["18Jun_latestCode_noPURW_v0"] = {

		"path_name": "rootfiles/Root_Files_18Jun_Full2013_allLatest_noPURW_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.93,
		"dy_corr": 0.95,
		"tt_corr": 1.17,

	}


	out_dict["23Jun_latestCode_tightJetID_v0"] = {

		"path_name": "rootfiles/Root_Files_23Jun_Full2013_allLatest_tightJetID_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}



	out_dict["23Jun_Full2013_MC_Madgraph_Photon_v0"] = {

		"path_name": "rootfiles/Root_Files_23Jun_Full2013_allLatest_MC_MadGraph_PhotonSele_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}


	out_dict["23Jun_Full2013_T2cc_PUVariations_v0"] = {

		"path_name": "rootfiles/Root_Files_23Jun_Full2013_allLatest_T2cc_PUVariations_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}


	out_dict["08Jul_Full2013_ISRRW_v0"] = {

		"path_name": "rootfiles/Root_Files_08Jul_Full2013_allLatest_ISRRW_v0/down",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["09Jul_Full2013_JES_v0"] = {

		"path_name": "rootfiles/Root_Files_09Jul_Full2013_allLatest_JES_v0/down",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["10Jul_Full2013_TT_v0"] = {

		"path_name": "rootfiles/Root_Files_10Jul_Full2013_allLatest_TTRW_v0/noweight",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["14Jul_Full2013_DYTesting"] = {

		"path_name": "rootfiles/Root_Files_14Jul_Full2013_allLatest_DYTesting_v5",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["25Jul_Full2013_30Threshes"] = {

		"path_name": "rootfiles/Root_Files_25Jul_Full2013_allLatest_30Threshes_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["28Jul_T2bw_skims_v0"] = {

		"path_name": "rootfiles/Root_Files_28Jul_T2bw_0p75_skims_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["31Jul_MuAsJet_v0"] = {

		"path_name": "rootfiles/Root_Files_31Jul_Full2013_muAsJet_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		# "wj_corr": 0.93,
		# "dy_corr": 0.93,
		# "tt_corr": 1.50,

		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["05Aug_CrossCheck_v0"] = {

		"path_name": "rootfiles/Root_Files_05Aug_Full2013_CrossCheck_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["07Aug_GenVeto_v0"] = {

		"path_name": "rootfiles/Root_Files_07Aug_GenVetoCrossCheck_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["17Aug_10GeVElectron_v0"] = {

		"path_name": "rootfiles/Root_Files_17Aug_Full2013_10GeVElectron_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.94,
		"dy_corr": 0.94,
		"tt_corr": 1.19,

	}

	out_dict["tmp"] = {

		"path_name": "rootfiles/tmp",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# new corrs from this set of files
		# "wj_corr": 0.91,
		# "dy_corr": 0.93,
		# "tt_corr": 1.16,

		# from Rob
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}

	out_dict["30Sep_withFailedSITV_v4"] = {

		"path_name": "rootfiles/Root_Files_30Sep_withFailedSITV_v4",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["17Oct_withInvertedMHTMET_v0"] = {

		"path_name": "rootfiles/Root_Files_17Oct_withInvertedMHTMET_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["23Oct_alphaT0p52_v0"] = {

		"path_name": "rootfiles/Root_Files_23Oct_alphaT0p52_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["23Oct_SMS_v0"] = {

		"path_name": "rootfiles/Root_Files_23Oct_SMS_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.91,
		"dy_corr": 0.93,
		"tt_corr": 1.16,

	}
	
	out_dict["22Oct_noMHTMET_v0"] = {

		"path_name": "rootfiles/Root_Files_22Oct_noMHTMET_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["30Oct_alphaT0p53_globalAlphaT_v0"] = {

		"path_name": "rootfiles/Root_Files_30Oct_alphaT0p53_globalAlphaT_v0",
		
		# All Runs
		# "had_lumi": 18.493,
		# "mu_lumi": 19.131,
		# "ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

		# # Run A
		# "had_lumi": 0.,
		# "mu_lumi": .685538,
		# "ph_lumi": .682937,


		# "wj_corr": 0.94,
		# "dy_corr": 1.06,
		# "tt_corr": 1.63,

		# # Run B
		"had_lumi": 4.412,
		"mu_lumi": 4.402,
		"ph_lumi": 4.402,


		# "wj_corr": 0.92,
		# "dy_corr": 0.91,
		# "tt_corr": 1.13,

		# # Run C
		# "had_lumi": 6.795,
		# "mu_lumi": 6.770,
		# "ph_lumi": 6.768,


		# "wj_corr": 0.93,
		# "dy_corr": 0.99,
		# "tt_corr": 1.31,

		# # Runs D
		# "had_lumi": 7.287,
		# "mu_lumi": 7.273,
		# "ph_lumi": 7.267,

		# "wj_corr": 0.91,
		# "dy_corr": 0.94,
		# "tt_corr": 1.19,

		# # Run ABC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.8575,
		# "ph_lumi": 11.8529,

		# "wj_corr": 0.93,
		# "dy_corr": 0.97,
		# "tt_corr": 1.26,

		# # Run BC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.172,
		# "ph_lumi": 11.17,

		# "wj_corr": 0.93,
		# "dy_corr": 0.96,
		# "tt_corr": 1.24,

	}

	out_dict["30Oct_alphaT0p53_v0"] = {

		"path_name": "rootfiles/Root_Files_30Oct_alphaT0p53_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

		# # Run A
		# "had_lumi": 0.,
		# "mu_lumi": .685538,
		# "ph_lumi": .682937,


		# "wj_corr": 0.94,
		# "dy_corr": 1.06,
		# "tt_corr": 1.63,

		# # Run B
		# "had_lumi": 4.412,
		# "mu_lumi": 4.402,
		# "ph_lumi": 4.402,


		# "wj_corr": 0.92,
		# "dy_corr": 0.91,
		# "tt_corr": 1.13,

		# # Run C
		# "had_lumi": 6.795,
		# "mu_lumi": 6.770,
		# "ph_lumi": 6.768,


		# "wj_corr": 0.93,
		# "dy_corr": 0.99,
		# "tt_corr": 1.31,

		# # Runs D
		# "had_lumi": 7.287,
		# "mu_lumi": 7.273,
		# "ph_lumi": 7.267,

		# "wj_corr": 0.91,
		# "dy_corr": 0.94,
		# "tt_corr": 1.19,

		# # Run ABC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.8575,
		# "ph_lumi": 11.8529,

		# "wj_corr": 0.93,
		# "dy_corr": 0.97,
		# "tt_corr": 1.26,

		# # Run BC
		# "had_lumi": 11.207,
		# "mu_lumi": 11.172,
		# "ph_lumi": 11.17,

		# "wj_corr": 0.93,
		# "dy_corr": 0.96,
		# "tt_corr": 1.24,

	}

	out_dict["03Nov_alphaT0p53_0p55_v1"] = {

		"path_name": "rootfiles/Root_Files_03Nov_alphaT0p53_0p55_v1",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["31Oct_MHTMET_mhtjet30_v0"] = {

		"path_name": "rootfiles/Root_Files_31Oct_MHTMET_mhtjet30_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["03Nov_alphaT0p55_0p6_v0"] = {

		"path_name": "rootfiles/Root_Files_03Nov_alphaT0p55_0p6_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["03Nov_alphaT0p6_0p7_v0"] = {

		"path_name": "rootfiles/Root_Files_03Nov_alphaT0p6_0p7_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["03Nov_alphaT0p7_v0"] = {

		"path_name": "rootfiles/Root_Files_03Nov_alphaT0p7_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	return out_dict[selector]
