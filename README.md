# Northern Hemisphere Merged and Gridded GPM and Atmospheric River Dataset README
October, 2023

## What is this?

Atmospheric rivers, often identified as regions of relatively high integrated water vapor transport, are found to enhance precipitation rates globally. This dataset contains precipitation and atmospheric water vapor content derived from the Global Precipitation Measurement (GPM) Core Observatory's Microwave Imager (GMI) brightness temperatures, gridded and spatio-temporally merged with at atmospheric river dataset (described in Mattingly et al. 2018; M18). The data starts at the beginning of the GPM record (launch in February 2014, first available data products in May 2014). 

## Data Packaging & Conversion:

The GPM satellite data are gridded and spatio-temporally matched to atmospheric rivers in the North Atlantic and North Pacific basins. All data is gridded to 0.25° × 0.25° (latitude × longitude) spatial resolution. Each timestep represents a GPM overpass through the basin matched to the nearest-time atmospheric river. All the data is compiled into monthly files of gridded observations.

Original data is converted to NetCDF-4 format for ease of sharing and compatibility within the academic community. The gridding and merging of datasets is performed using Python. The monthly files are compressed into year and basin: either the North Atlantic (NA) or the North Pacific (NP) (e.g., NA_2014) and zipped. The files have the basin name indicated and are by year and month (e.g., gridded_atlantic_201405.nc). 

## Internal Structure of NetCDF Files:

Spatial & Temporal Variables: Lat/Lon and Time
Data Variables: GPM GPROF surface precipitation rates,  GPM atmospheric water vapor content, and M18 Atmospheric Rivers
Note: Each monthly file contains ~250 time steps. Missing data is marked as -9999.

## Data Description:

Files are monthly and available for the North Atlantic and North Pacific basins. Files contain gridded GPM GPROF surface precipitation rates and atmospheric water vapor content, with an atmospheric river flag. Each time step represents a single GPM overpass through the basin (N. Atlantic or N. Pacific). 

## Quality Assurance:

A quality assurance (QA) procedure has been undertaken to ensure the integrity of the data. Post QA, the data is transformed into daily NetCDF-4 files following the Climate and Forecast (CF) conventions (version 1.10) and compressed with a level 2 deflation for optimized file size.

## Filename Convention:

The naming convention for the NetCDF files is structured as follows:
gridded_<basin>_YYYYMM.nc

Where:

    basin: 'atlantic' or 'pacific'
    YYYYMM: Month (YearMonth)

## Directory Structure:

SITE_YEAR/
|-- netCDF/
|   |-- Atlantic/
|   |   |-- gridded_atlantic_YYYYMM.nc
|   |-- Pacific/
|   |   |-- gridded_pacific_YYYYMM.nc


## Use and Access: 

These data are made available under a Creative Commons Attribution Non-Commercial license 
(CC BY 4.0).


## Contact:

For any further questions or assistance with the dataset, please reach out to the corresponding data authors (Marian Mateling) via email: mateling@wisc.edu or (Claire Pettersen) via email: pettersc@umich.edu

## Date of last update:

October 16, 2023
