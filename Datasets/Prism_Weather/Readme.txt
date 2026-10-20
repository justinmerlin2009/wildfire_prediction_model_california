Readme

PRISM (Parameter-elevation Regressions on Independent Slopes Model) data is a high-resolution, gridded spatial climate dataset for the United States, developed by Oregon State University. It provides daily, monthly, and 30-year normal data (1895–present) for precipitation, temperature (max/min/mean), and dewpoint. It is widely used to understand weather patterns and climate, particularly in areas with complex, mountainous terrain. 
Oregon State University

What is PRISM Data?
Coverage: Primarily the conterminous United States, with some data for Alaska, Hawaii, and Pacific territories.
Resolution: 
Resolution: Available at 4km (
2.5
2
.
5
 arc-min) and 800m (
30
3
0
-arc-sec) spatial resolutions.
0
-arc-sec) spatial resolutions.
Variables: Precipitation (ppt), Min/Max/Mean Temperature (tmin/tmax/tmean), Dewpoint (tdmean), and Vapor Pressure Deficit (vpdmin/vpdmax).
Types:
30-Year Normals (Normals): Average values for 30-year periods (e.g., 1991–2020).
All-Networks (AN): Daily and monthly data incorporating all available station data and radar.
Long-Term (LT): Monthly data for analyzing decadal-scale variations. 
Oregon State University
Oregon State University
 +1
How is PRISM Data Collected?
PRISM utilizes "expert system" modeling that combines point measurements from roughly 20,000 stations (NOAA, CoCoRaHS, USDA, etc.) with a digital elevation model. 
Climate Data Guide
Climate Data Guide
 +1
Data Ingestion: Gathers daily, monthly, and annual in-situ point measurements.
Physiographic Weighting: Uses a weighted regression to account for elevation, slope aspect, rain shadows, temperature inversions, and coastal proximity.
Radar Incorporation: East of the Rockies, station data is supplemented with AHPS NEXRAD radar analyses.
Quality Control (QC): Includes range checks, spatial consistency, and manual review of grids.
Re-running: The data is re-run up to 8 times over 6 months to include updated station data, making it "stable". 
Climate Data Guide
Climate Data Guide
Where to Download PRISM Data
Data can be downloaded for free from the official PRISM Climate Group website. 
Oregon State University
Oregon State University
Web Portal (Explorer): prism.oregonstate.edu/explorer/ — Best for finding specific locations, viewing maps, and downloading time series.
FTP/Data Directory: data.prism.oregonstate.edu/ — Best for bulk downloads of daily/monthly data.
Web Services: prism.oregonstate.edu/downloads/ — Automated retrieval via API (data in BIL/ASCII/CSV formats).
R Package: The prism R package can be used to download, organize, and visualize the data. 
Oregon State University
Oregon State University
 +5
Note: As of March 2025, both 4km and 800m data are available for free to the public, although some highly specialized or large datasets might require fees for tailored, high-resolution orders. 
Oregon State University
Oregon State University