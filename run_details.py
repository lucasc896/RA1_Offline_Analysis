def this_run():

	selector = "28Jan_globalAlphaT"

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

	out_dict["tmp"] = {

		"path_name": "rootfiles/tmp",
		
		# All Runs
		"had_lumi": 18.493,
		"mu_lumi": 19.131,
		"ph_lumi": 19.12,

		"wj_corr": 1.01,
		"dy_corr": 0.53,
		"tt_corr": 1.30,

		#testing values from 19Dec run!!
		# "wj_corr": 0.92,
		# "dy_corr": 0.97,
		# "tt_corr": 1.22,


	}

	return out_dict[selector]
