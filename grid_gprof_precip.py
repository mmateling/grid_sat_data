# ---------------------------------------------------------------------------------------
#
#	grid_gprof_precip
#
#	Author: Marian Mateling (mateling@wisc.edu)
#
#	Read in one GMI GPROF file: read_one_file()
#
#	Grid precipitation data (Conditional gridbox mean >= 0.01 mm/h)
#
#	Input includes AR_flag and AR datelist information to create a grid of
#	"counts", or number of GPM satellite footprints, during AR and no AR instances
#
#	AR data is 6-hourly, 0.25x0.25 deg grid (Mattingly et al. 2018)
#
# ---------------------------------------------------------------------------------------

import numpy as np
import h5py
from glob import glob
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------------

# year, month, day, = int
# region = 'atlantic' or 'pacific' 
# ar_flag (3D: time, lat, lon), ar_dates (1D: time)

def readin_precip(year, month, day, region, ar_flag, ar_dates):

	precip, sfc_type, lat, lon, year, month, day, hour, minute = \
			read_one_file(filename)
		
      # Calls gprof_grid_region()
	try:
		datelist, region_precip, surface_flag, counts, \
		pr_0, pr_0p1, pr_0p5, pr_1, ar_flag = \
		gprof_grid_region(precip, sfc_type, year, month, \
		day, hour, minute, lat, lon, region, ar_flag, ar_dates)
	except:
		print('Region not in file')



# ---------------------------------------------------------------------------------

# Reads one GMI GPROF file

def read_one_file(filename):

	f = h5py.File(filename, 'r')	
		
	l1c = f['/S1/L1CqualityFlag'][:]
	qflag = f['/S1/qualityFlag'][:]
	pixel = f['/S1/pixelStatus'][:]

	mask = np.logical_and(np.logical_and(qflag != 0, l1c != 0), pixel != 0)

	precip = np.ma.masked_where(mask, f['/S1/surfacePrecipitation'][:])
	sfc_type = np.ma.masked_where(mask, f['/S1/surfaceTypeIndex'][:])
	
	year = f['/S1/ScanTime/Year'][:]
	month = f['/S1/ScanTime/Month'][:]
	day = f['/S1/ScanTime/DayOfMonth'][:]	
	hour = f['/S1/ScanTime/Hour'][:]	
	minute = f['/S1/ScanTime/Minute'][:]			
	lat = f['/S1/Latitude'][:]
	lon = f['/S1/Longitude'][:]

	f.close()

	return precip, sfc_type, lat, lon, year, month, day, hour, minute

# ---------------------------------------------------------------------------------

# Takes one file of data and grids within defined region
#   gridbox mean precipitation is conditional >= 1E-2 mm/h

def gprof_grid_region(precip, sfc_type, year, month, day, hour, \
	minute, lat, lon, region, ars, ar_dates):

	# Atlantic: 45-70 North,  -70 W to  10 E
	# Pacific:  45-70 North, 140 E to -120 W

	if region == 'atlantic':
		lat_min = 45; lat_max = 70; lon_min = -70; lon_max = 10
		lons = np.arange(-70, 10.25, 0.25)
	elif region == 'pacific':
		lat_min = 45; lat_max = 70
		# The "min" is the LHS, or 155 East.
		lon_min = 140; lon_max = -120
		lons = np.concatenate((np.arange(140, 180.25, 0.25), \
			np.arange(-179.75, -119.75, 0.25)))

	lats = np.arange(45, 70.25, 0.25)		

      # Create several latxlon  arrays

       # Add up footprints within gridbox	
	region_counts = np.zeros([len(lats)-1, len(lons)-1])
	AR_counts = np.zeros([len(lats)-1, len(lons)-1])
	noAR_counts = np.zeros([len(lats)-1, len(lons)-1])

       # Add up footprints within gridbox for precip 
       # rates >0, 0.1, 0.5, 1.0 mm/h
	pr_0 = np.zeros([len(lats)-1, len(lons)-1])
	pr_0p1 = np.zeros([len(lats)-1, len(lons)-1])
	pr_0p5 = np.zeros([len(lats)-1, len(lons)-1])
	pr_1 = np.zeros([len(lats)-1, len(lons)-1])

       # Add up footprints within gridbox during AR
	ARpr_0 = np.zeros([len(lats)-1, len(lons)-1])
	ARpr_0p1 = np.zeros([len(lats)-1, len(lons)-1])
	ARpr_0p5 = np.zeros([len(lats)-1, len(lons)-1])
	ARpr_1 = np.zeros([len(lats)-1, len(lons)-1])

       # Add up footprints within gridbox during no AR
	noARpr_0 = np.zeros([len(lats)-1, len(lons)-1])
	noARpr_0p1 = np.zeros([len(lats)-1, len(lons)-1])
	noARpr_0p5 = np.zeros([len(lats)-1, len(lons)-1])
	noARpr_1 = np.zeros([len(lats)-1, len(lons)-1])
	
	
	# For each file/swath, find each lat/lon box's data and mask outside.
	try:
		if region == 'atlantic':
		
			x0, y0 = np.ma.where(np.ma.logical_and(np.ma.logical_and(lat \
			>= lat_min, lat < lat_max), np.ma.logical_and(lon >= lon_min, \
			lon < lon_max)))
				
		elif region == 'pacific':
		
		    #  For PACIFIC, the next lines need logical_or 
		    #   for lons (greater than 155 OR less than -130)
		
			x0, y0 = np.ma.where(np.ma.logical_and(np.ma.logical_and(lat \
			>= lat_min, lat < lat_max), np.ma.logical_or(lon >= lon_min, \
			lon < lon_max)))
	except:
		# No data within the region
		return 
			
			
	# If there is GMI data in the region			
	if len(x0) > 0 and len(y0) > 0:
		
		# Create arrays latxlon filled with -9999
		swath_precip = np.ma.zeros([len(lats)-1, len(lons)-1]) - 9999
		swath_sfc_flag = np.ma.zeros([len(lats)-1, len(lons)-1]) - 9999
		swath_ar_flag = np.ma.zeros([len(lats)-1, len(lons)-1]) - 9999
						
		times = []
			
		# For each 0.25 degree latitude/longitude box
		for i in range(len(lats)-1):
			for j in range(len(lons)-1):
			
				# Find individual gridbox, where: i=lat j=lon
				if lons[j] == 180:					
					try:
						x, y = np.ma.where(np.ma.logical_and(\
						np.ma.logical_and(lat >= lats[i], \
						lat < lats[i+1]), np.ma.logical_or(\
						abs(lon) == lons[j], lon < -179.75)))
					except:
						continue			
				else:	
					try:
						x, y = np.ma.where(np.ma.logical_and(\
						np.ma.logical_and(lat >= lats[i], \
						lat < lats[i+1]), np.ma.logical_and(\
						lon >= lons[j], lon < lons[j+1])))
					except:
						continue
		
				# Check that there's data; if not, then pass this.
				if len(x) > 0 and len(y) > 0:

					# --------------------------------
					# Bin all GPROF data that falls within
					#  the defined gridbox
						
					prec_list = np.ma.masked_less([precip[w][z] \
						for w,z in zip(x,y)], 0.0)
							
						 
					# Conditional gridbox mean >= 0.01 mm/h
					precip_min = 1E-2
						
					swath_precip[i][j] = \
						np.ma.mean(np.ma.masked_invalid(\
						np.ma.masked_less(prec_list, precip_min)))
			
					if len(x) != len(y):
						print('issue with counting')
					
					# Flag surface types					
					swath_sfc_flag[i][j] = check_ocean_only(sfc_type, x, y)
					
					# (Includes over-land data, hence sfc flag >= 0)					
					
					if swath_sfc_flag[i][j] >= 0:
					
					      # Number of footprints
						region_counts[i][j] += np.ma.masked_less(prec_list, 0.).count()
					
					      # Number of footprints when precip > 0, >= 0.1, >= 0.5, >= 1.0
						aa = np.ma.masked_less_equal(prec_list, 0.).count()
						bb = np.ma.masked_less(prec_list, 0.1).count()
						cc = np.ma.masked_less(prec_list, 0.5).count()
						dd = np.ma.masked_less(prec_list, 1.0).count()
						
						
						pr_0[i][j] += aa
						pr_0p1[i][j] += bb
						pr_0p5[i][j] += cc
						pr_1[i][j] += dd
							
					for w in x:
						times.append(datetime(year[w], month[w], \
						day[w], hour[w], minute[w]))
					
					# ** Each overpass should start and end within the same 6 hours (same AR timestep) **
					
					swath_ar_flag[i][j] = create_ar_flag(times[0], ar_datelist, ars, \
						swath_sfc_flag[i][j], i, j)
					
					# If there's an AR here, add counts to 'AR'
					if swath_ar_flag[i][j] == 1 and swath_sfc_flag[i][j] >= 0:
					
						AR_counts[i][j] += np.ma.masked_less(prec_list, 0.).count()
						ARpr_0[i][j] += aa
						ARpr_0p1[i][j] += bb
						ARpr_0p5[i][j] +=  cc
						ARpr_1[i][j] += dd
						
					# If there's an No AR here, add counts to 'No AR'					
					elif swath_ar_flag[i][j] == 0 and swath_sfc_flag[i][j] >= 0:
					
						noAR_counts[i][j] += np.ma.masked_less(prec_list, 0.).count()
						noARpr_0[i][j] += aa
						noARpr_0p1[i][j] += bb
						noARpr_0p5[i][j] +=  cc
						noARpr_1[i][j] += dd

				else:
					# Leave inds[i][j] = -9999 for swath_precip, swath_sfc_flag, swath_ar_flag
					continue
			
		min_time = min(times)  # Start of swath
		max_time = max(times)  # End of swath
			
		# For each overpass, assign one datetime (midpoint of overpass thru region)
		datelist = min_time + (max_time - min_time)/2	
			
		return datelist, swath_precip, swath_sfc_flag, region_counts, pr_0, pr_0p1,\
		pr_0p5, pr_1, AR_counts, ARpr_0, ARpr_0p1, ARpr_0p5, ARpr_1,\
		noAR_counts, noARpr_0, noARpr_0p1, noARpr_0p5, noARpr_1, swath_ar_flag

			
	else:
		# No data from this file falls within defined region
		return 
		
# ---------------------------------------------------------------------------------
	
"""
 For each grid box, this function will make a list of each value of sfc_type. 
  Then, it looks for any values > 1. 

 Surface flag: 
   100% over ocean [sfc_type = 1]   = ocean [return 0]
   100% over land [sfc_type = 3-12] = land [return 1]
   Mixture ocean + land  	    = mixed [return 2]

 Account for masked pixels. If all pixels are <= 1, then
    we will call the whole grid box ocean. If no pixels are ocean values,
    i.e. along the edge of the swath, return other.	
"""


def check_ocean_only(sfc_type, x, y):

      # List all sfc_type vals
	sfc_type_list = np.ma.asarray([np.ma.masked_less(sfc_type[w][z], 0) \
		for w,z in zip(x,y)], dtype=object).data

			
      # If all data has sfc_flag <= 1
	if np.ma.all(np.ma.less_equal(sfc_type_list, 1)):
		return 0

      # If all data has sfc_flag > 1
	elif np.ma.all(np.ma.greater(sfc_type_list, 1)):
		return 1

      # If data has *both* sfc_flag <= 1 and sfc_flag > 1
	elif np.ma.any(np.ma.greater(sfc_type_list, 1)) and \
		np.ma.any(np.ma.less_equal(sfc_type_list, 1)):
		return 2
		
      # Missing data
	else:
		return -9999
		
		
# ------------------------------------------------------------------------------

# Using the nearest timestep from the AR database, match each GPROF basin
#   with a gridded AR flag. 1 = AR, 0 = No AR

def create_ar_flag(gprof_datelist, ar_datelist, ars, sfc_flag, i, j):

        # Now, just use one value to assign entire gridbox an AR value.


        ar_date = nearest(ar_datelist, gprof_datelist)
        ar_index = ar_datelist.index(ar_date)
        ar_flag_0 = ars[ar_index][i][j]

        # Including over-land data (sfc >= 0)                                      

        if sfc_flag < 0:
                ar_flag_0 = -9999

        return ar_flag_0


# ------------------------------------------------------------------------------        

def nearest(items, pivot):

        return min(items, key=lambda x: abs(x - pivot))
