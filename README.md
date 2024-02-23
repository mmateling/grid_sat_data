# Code to grid GMI GPROF precipitation data and merge with an Atmospheric River Dataset
February 2024

Given a regularly-gridded AR dataset (dimensions = time, lat, lon), the grid_gprof_precip.py script searches [2A GMI GPROF](https://gpm.nasa.gov/resources/documents/gpm-gprof-algorithm-theoretical-basis-document-atbd) files for data within the pre-defined boundaries of a region ('atlantic' and 'pacific') for a specified date. For each file, if data falls within the region, the 2A GMI GPROF precipitation rates are gridded and spatio-temporally matched to atmospheric rivers in the North Atlantic and North Pacific basins. All data is gridded to 0.25° × 0.25° (latitude × longitude) spatial resolution, using the conditional mean (>= 0.01 mm/h) GPROF precipitation rate for each gridbox. Each timestep represents a GPM satellite overpass through the basin matched to the nearest-time atmospheric river. Missing data is marked as -9999.

[Merged, gridded GPM-AR dataset repository](https://doi.org/10.7302/7t62-s085)

[Repository for Mattingly et al. (2018) AR algorithm](https://github.com/ksmattingly/AR_alg_v2) used as input (AR flags and date/time information)

(Mateling et al., in prep)

## Input

  - year, month, day, = integers
  - region = 'atlantic' or 'pacific'
  - ar_flag (3D: time, lat, lon)
  - ar_dates (1D: time)

## Output
For one day, in specified region ('atlantic' or 'pacific')
(time) = number of GPM-CO overpasses through the defined region; varies daily
  - datelist = (time)
  - region_precip (time, lat, lon)
  - surface_flag (lat, lon)
  - counts (lat, lon) = GMI footprints per gridbox
  - pr_0 = Counts of Precip > 0 mm/h
  - pr_0p1 = Counts of Precip >= 0.1 mm/h
  - pr_0p5 = Counts of Precip >= 0.5 mm/h
  - pr_1 = Counts of Precip >= 1.0 mm/h
  - ar_flag (lat, lon)

## Dependencies

This code requires a python 3 environment with the following packages:
  - numpy
  - h5py
  - glob
  - datetime

## Contact:

For any further questions or assistance with the dataset, please reach out to the corresponding data authors (Marian Mateling) via email: mateling@wisc.edu or (Claire Pettersen) via email: pettersc@umich.edu

