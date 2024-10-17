old usage notes at the top of `cmor_mixer.py`

# Before start this script in common way run these 2 command in terminal where you are going to execute this script:
#     module load python/3.9
#     conda activate cmor

# another possible runs without any preparation in terminal:
#    /home/san/anaconda/envs/cmor_dev/bin/python
#    /app/spack/v0.15/linux-rhel7-x86_64/gcc-4.8.5/python/3.7.7-d6cyi6ophaei6arnmzya2kn6yumye2yl/bin/python


# How to run it (simple examples):
# ~/fms_yaml_tools/CMOR_3/cmor_mixer.py
#   -d /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_1pctCO2_C/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/monthly/5yr
#   -l /home/san/CMOR_3/GFDL-CM4_1pctCO2_C_CMOR-Amon.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_Amon.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_CM4_1pctCO2_C.json

# ~/fms_yaml_tools/cmor_mixer.py
#	-d /archive/Fabien.Paulot/ESM4/H2/ESM4_amip_D1_soilC_adj/gfdl.ncrc3-intel16-prod-openmp/pp/land/ts/monthly/5yr
#   -l /home/san/CMOR_3/GFDL-ESM4_amip_CMOR-landCML.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_Lmon.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_amip.json

# ~/fms_yaml_tools/cmor_mixer.py
#   -d /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_historical/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/monthly/5yr
#   -l /home/san/CMOR_3/GFDL-CM4_historical_CMOR-Amon.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/Atmos_Monthly.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_CM4_historical.json

# ~/fms_yaml_tools/cmor_mixer.py
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/daily/5yr
#   -l /home/san/CMOR_3/GFDL-ESM4_CMOR-day_historical.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_day.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json
#   -o /net2/san

# ~/fms_yaml_tools/cmor_mixer.py
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos/ts/6hr/5yr
#   -l /home/san/CMOR_3/GFDL-ESM4_CMOR-6hr.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_6hrPlev.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json

# ~/fms_yaml_tools/cmor_mixer.py
#   -d /archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_historical_D1/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/3hr/5yr
#   -l /home/san/CMOR_3/GFDL_ESM4_historical_CMOR-3hr.lst
#   -r /home/san/CMOR/cmor/cmip6-cmor-tables/Tables/CMIP6_3hr.json
#   -p /home/san/CMOR/cmor/Test/CMOR_input_ESM4_historical.json
#   -o /net2/san

# Additional tables containing in /home/san/CMIP6_work/cmor/cmip6-cmor-tables/Tables:
#    CMIP6_CV.json
#    CMIP6_formula_terms.json
#    CMIP6_grids.json
#   CMIP6_coordinate.json

# Detailed description of program is placed at
#    https://docs.google.com/document/d/1HPetcUyrVXDwCBIyWheZ_2JzOz7ZHi1y3vmIlcErYeA/edit?pli=1

# Keep in mind rule for input ../cmor/cmip6-cmor-tables/Tables/*.json:
#    output variables can not contain "_" in out_name, though name (and standard_name) itself can have it; example:
#        "alb_sfc": {
#            "frequency": "mon",
#            "modeling_realm": "atmos",
#            "standard_name": "alb_sfc",
#            "units": "percent",
#            "cell_methods": "area: time: mean",
#            "long_name": "surface albedo",
#            "comment": "",
#            "dimensions": "longitude latitude time",
#            "out_name": "albsfc",
#            "type": "real",
#            "positive": "",
#            "valid_min": "",
#            "valid_max": "",
#            "ok_min_mean_abs": "",
#            "ok_max_mean_abs": ""
#        }

# Problems with standard CMOR library:
#   - monthly variable "enth_conv_col" produces error - CMOR expects 4 dimensions but it has only 3;
#   - variable /archive/oar.gfdl.cmip6/CM4/warsaw_201710_om4_v1.0.1/CM4_historical/gfdl.ncrc4-intel16-prod-openmp/pp/atmos_cmip/ts/3hr/5yr/atmos_cmip.1965010100-1969123123.clt.nc
#     is not readable.
