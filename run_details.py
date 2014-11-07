def this_run():

	selector = "06Nov_fineJetMulti_alphaT_0p53_v0"

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

		"wj_corr": 0.92,
		"dy_corr": 0.96,
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
		#"had_lumi": 6.795,
		#"mu_lumi": 6.770,
		#"ph_lumi": 6.768,


		#"wj_corr": 0.93,
		#"dy_corr": 0.99,
		#"tt_corr": 1.31,

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

		"wj_corr": 0.92,
		"dy_corr": 0.97,
		"tt_corr": 1.22,

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

	
	out_dict["18March_fineJetMulti"] = {

		"path_name": "rootfiles/Root_Files_18March_Full2013_noISRRW_SITV_fixedXS_allNewMu_fineJetMulti_v2",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# le3j
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.18,
	
		# eq2j
		"wj_corr": 0.97,
		"dy_corr": 0.98,
		# "tt_corr": 1.20, # 3j
		# "tt_corr": 1.15, # rob
		"tt_corr": 1.05, # 3j, 1b
	}

	out_dict["05March_Rob_NotSure"] = {

		"path_name": "rootfiles/Root_Files_05March_Full2013_notSure_IC_Rob",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# le3j
		"wj_corr": 0.92,
		"dy_corr": 0.93,
		"tt_corr": 1.18,
	}


	out_dict["tmp"] = {

		"path_name": "rootfiles/tmp",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# "wj_corr": 1.01,
		# "dy_corr": 0.53,
		# "tt_corr": 1.30,

		#testing values from 19Dec run!!
		"wj_corr": 0.92,
		"dy_corr": 0.97,
		"tt_corr": 1.22,


	}

	out_dict["04Nov_fineJetMulti_v0"] = {

		"path_name": "rootfiles/Root_Files_04Nov_fineJetMulti_v0",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		# taken from parked final (change if necessary)
		"wj_corr": 0.93,
		"dy_corr": 0.94,
		"tt_corr": 1.18,

	}

	out_dict["06Nov_fineJetMulti_alphaT_0p53_v0"] = {

		"path_name": "rootfiles/Root_Files_06Nov_fineJetMulti_alphaT_0p53_v0",
		
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
