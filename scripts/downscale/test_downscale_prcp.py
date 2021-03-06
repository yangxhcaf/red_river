'''
Script for and prototyping and testing precipitation downscaling approaches.
'''

from esd.downscale.prcp import setup_data_for_analog, downscale_analog_anoms, \
    downscale_analog, downscale_analog_nonzero_scale, downscale_analog_anoms_sgrid,\
    PrcpDownscale
import esd
import numpy as np
import os
import pandas as pd
import xarray as xr
from esd.downscale.common import _convert_times

if __name__ == '__main__':
    
    fpath_prcp_obs = esd.cfg.fpath_aphrodite_prcp
    fpath_prcp_obsc = os.path.join(esd.cfg.path_aphrodite_resample,
                                   'aprhodite_redriver_pcp_1961_2007_p25deg_remapbic.nc')
    fpath_prcp_mod = fpath_prcp_obsc
    
    base_start_year = '1961'
    base_end_year = '1990'
    downscale_start_year = '1991'
    downscale_end_year = '2007'
        
#     base_start_year = '1978'
#     base_end_year = '2007'
#     downscale_start_year = '1961'
#     downscale_end_year = '1977'
         
    ds_data,win_masks = setup_data_for_analog(fpath_prcp_obs, fpath_prcp_obsc,
                                              fpath_prcp_mod,
                                              base_start_year, base_end_year,
                                              downscale_start_year, downscale_end_year)
     
    mod_downscale_anoms = downscale_analog_anoms(ds_data, win_masks)
    
    prcp_d = PrcpDownscale(fpath_prcp_obs, fpath_prcp_obsc, base_start_year, base_end_year, base_start_year,base_end_year,downscale_start_year,downscale_end_year)
    da_mod = xr.open_dataset(fpath_prcp_mod).PCP#xr.open_dataset(fpath_prcp_mod).PCP.loc[downscale_start_year:downscale_end_year]
    da_mod['time'] = _convert_times(da_mod)
    #da_mod = da_mod.loc[downscale_start_year:downscale_end_year]
    mod_downscale_anoms2 = prcp_d.downscale(da_mod)
    
    
    mod_downscale = downscale_analog(ds_data, win_masks)
    
#    mod_downscale_anoms = downscale_analog_anoms_noscale(ds_data, win_masks)
#    mod_downscale = downscale_analog_noscale(ds_data, win_masks)
    
    sgrid_mod_downscale_anoms = downscale_analog_anoms_sgrid(ds_data, win_masks)
    sgrid_mod_downscale = downscale_analog_nonzero_scale(ds_data, win_masks) 
     
    da_obsc = xr.open_dataset(fpath_prcp_obsc).PCP.load()
    da_obsc['time'] = pd.to_datetime(da_obsc.time.to_pandas().astype(np.str),
                                     format='%Y%m%d', errors='coerce')
    mod_downscale_cg = da_obsc.loc[downscale_start_year:downscale_end_year]
         
    mod_downscale_anoms.name = 'mod_d_anoms'
    mod_downscale.name = 'mod_d'
    sgrid_mod_downscale_anoms.name = 'mod_d_anoms_sgrid'
    sgrid_mod_downscale.name = 'mod_d_sgrid'
    mod_downscale_cg.name = 'mod_d_cg'
     
    obs = ds_data.obs.loc[downscale_start_year:downscale_end_year]
     
    ds_d = xr.merge([obs, mod_downscale_cg, mod_downscale, mod_downscale_anoms,
                     sgrid_mod_downscale, sgrid_mod_downscale_anoms])
    ds_d = ds_d.drop('month')
    ds_d.to_netcdf(os.path.join(esd.cfg.data_root,'downscaling',
                                'downscale_tests_%s_%s.nc'%(downscale_start_year,
                                                            downscale_end_year)))
