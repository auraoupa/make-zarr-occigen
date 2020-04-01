#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dask_jobqueue import SLURMCluster 
from dask.distributed import Client 
  
cluster = SLURMCluster(cores=28,name='make_profiles',walltime='00:30:00',job_extra=['--constraint=HSW24','--exclusive','--nodes=1'],memory='120GB',interface='ib0') 
cluster.scale(280)
cluster

from dask.distributed import Client
client = Client(cluster)
client


# In[2]:


get_ipython().system('squeue -u albert7a')

import time
nb_workers = 0
while True:
    nb_workers = len(client.scheduler_info()["workers"])
    if nb_workers >= 2:
        break
    time.sleep(1)
print(nb_workers)


# In[3]:


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

import zarr

get_ipython().run_line_magic('matplotlib', 'inline')


# In[4]:


files=sorted(glob.glob('/store/CT1/hmg2840/lbrodeau/eNATL60/eNATL60-BLB002*-S/*/eNATL60*gridT-2D*nc'))
for file in files:
    print(file)


# In[5]:


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


# In[6]:


ds = xr.open_mfdataset(files, parallel=True, **open_kwargs)


# In[7]:


template = xr.open_dataset(files[0], decode_cf=False, decode_times=False)

ds["nav_lat"] = template["nav_lat"]

ds["nav_lon"] = template["nav_lon"]

ds

del template


# In[8]:


ds


# In[9]:


compressor = numcodecs.Blosc(cname='snappy', clevel=6, shuffle=-1)
encoding = {vname: {'compressor': compressor} for vname in ds.variables}


# In[10]:


outdir = '/store/albert7a/eNATL60/zarr/eNATL60-BLB002-SSH-1h'
ds = ds.chunk(chunks=dict(time_counter=240, y=240, x=480))
ds.to_zarr(outdir, encoding=encoding, mode="w")

 


# In[ ]:




