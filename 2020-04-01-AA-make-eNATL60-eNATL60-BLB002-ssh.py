#!/usr/bin/env python


import warnings
warnings.filterwarnings("ignore")
import dask 
import numpy as np
import xarray as xr
import time
import os 
import time 
import glob
import numcodecs
import datetime
import zarr




files=sorted(glob.glob('/store/CT1/hmg2840/lbrodeau/eNATL60/eNATL60-BLB002*-S/*/eNATL60*gridT-2D*nc'))
for file in files:
    print(file)




# these are variables I just want to drop forever

drop_vars = ['nav_lat', 'nav_lon', 'somxl010', 'sosaline', 'sosstsst']
extra_coord_vars = ['time_counter', 'y', 'x']
extra_coord_vars = []
chunks = dict(time_counter=1)
open_kwargs = dict(drop_variables=(drop_vars + extra_coord_vars),
                   chunks=chunks,
                   decode_cf=True,
                   decode_times=False,
                   concat_dim="time_counter")  #, combine='nested')



ds = xr.open_mfdataset(files, parallel=True, **open_kwargs)



template = xr.open_dataset(files[0], decode_cf=False, decode_times=False)

ds["nav_lat"] = template["nav_lat"]

ds["nav_lon"] = template["nav_lon"]

ds

del template



ds



compressor = numcodecs.Blosc(cname='snappy', clevel=6, shuffle=-1)
encoding = {vname: {'compressor': compressor} for vname in ds.variables}



outdir = '/store/albert7a/eNATL60/zarr/eNATL60-BLB002-SSH-1h-new'
ds = ds.chunk(chunks=dict(time_counter=240, y=240, x=480))

print (str(datetime.datetime.now()))
ds.to_zarr(outdir, encoding=encoding, mode="w")
print (str(datetime.datetime.now()))

 





