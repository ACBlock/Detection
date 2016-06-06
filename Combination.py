
# coding: utf-8

# # Outline
#
# + Align images based on WCS.
# + Measure sky background (something quick and easy, not sophisticated and likely to not work).
# + Subtract sky background from each image.
# + Save subtracted images.
# + Combine images in the same filter, adjusting for differences in pointing.
# + save combined images.
#

# ## To install before you start:
#
# + `conda install -c astropy reproject`
# + `pip install --upgrade --no-deps msumastro`

# In[1]:

import os

import numpy as np

from astropy.coordinates import SkyCoord
from astropy.io import fits

from ccdproc import CCDData, Combiner

# Region to use for sky backgraound
# Top left corner:
top_left = SkyCoord("21h41m25.438s +00d44m32.55s")
bottom_right = SkyCoord("21h41m30.875s +00d41m05.14s")
# mean was -21.94


# In[2]:

# the other rectangle
top_left = SkyCoord("21h42m05.971s +00d38m10.12s")
bottom_right = SkyCoord("21h42m15.941s +00d35m12.23s")
# mean -20.892


# In[3]:

from reproject import reproject_interp
from msumastro import ImageFileCollection


# ## Change `image_dir` below to the appropriate location
#

# In[4]:

image_dir = 'C:/Users/Andy-PC/Documents/Research/7-20-15 Reduced With Darks/V Filter'
ic = ImageFileCollection(image_dir, keywords='*')


# ### Edit filters as needed

# In[5]:

filters = ['V']


# ## Change object name (or remove it) and adjust filter if needed

# In[6]:

# Use the middle image as the reference WCS

files = ic.files_filtered(filter='V', object='sa113')
files


# In[7]:

ref_file = files[len(files)//2]
reference_image = fits.getheader(os.path.join(ic.location, ref_file))


# ## NEW IMAGES ARE SAVED TO SAME DIRECTORY AS NOTEBOOK
#
# So change the `save_location` if you don't want that.
#
# The Wise Astronomer also adjusts the object if necessary.

# In[9]:

for filt in filters:
    for hdu in ic.hdus(filter=filt, object='sa113', save_location='C:/Users/Andy-PC/Documents/Research/Combined Images/7-20-15combined/7-20-15 with darks scaled/V filter'):
        new_data, footprint = reproject_interp(hdu, reference_image)
        hdu.data = new_data


# In[10]:

ic_new = ImageFileCollection('C:/Users/Andy-PC/Documents/Research/Combined Images/7-20-15combined/7-20-15 with darks scaled/V filter', keywords='*')


# In[11]:

def combine_filter(image_collection, filter=None):
    ccd_list = []
    for hdu in ic_new.hdus(filter=filter):
        masked_data = np.ma.array(hdu.data, mask=np.isnan(hdu.data))
        med = np.ma.median(masked_data)
        print(med)
        ccd_list.append(CCDData(hdu.data - med, meta=hdu.header, unit='adu', mask=np.isnan(hdu.data)))
    c = Combiner(ccd_list)
    foo = c.average_combine()
    return foo


# In[12]:

for filt in filters:
    combined_image = combine_filter(ic_new, filter=filt)
    combined_image.header['filter'] = filt
    combined_image.write(filt + '_combined.fit')
