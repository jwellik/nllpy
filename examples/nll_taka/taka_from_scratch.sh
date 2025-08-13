#!/bin/bash

################################################################
#
# This example shows how to create a NonLinLoc control file
# and run NonLinLoc given FDSN urls for events and station
# inventories.
#
# This example focuses on a swarm of earthquakes near Tanaga,
# Takawangha, and Kanaga volcanoes in Alaska. The time period
# of interest is February 13, 2023.
#
# The steps taken are:
# - Download events with arrival information
#   - NOTE: There are a few issues that require this step to be a bit hack-ish:
#       1) The FDSN Event API does not currently support retrieving arrival information (Solution: Retrieve via ObsPy)
#       2) Many phase hints are stored as '?' (Solution: Assign as 'P' or 'S' based on channel code)
#       3) NonLinLoc does not read QuakeML format (Solution: Write to NLLOC_OBS w ObsPy)
# - Create NLL control file
#   - volcano lat,lon,elevation
#   - FDSN url (station inventory)
# - Run NonLinLoc (requires prior NLL installation)
#   - Vel2Grid, Grid2Time, NLLoc
# - Plot results
#
# This example requires that NonLinLoc is installed and working.
#
################################################################

# Welcome message
echo "NLLPy example for Takawangha Volcano, Alaska"
echo ""

# First, remove output folders and files if they already exist
echo "Remove output directories and files from previous runs, if they exist..."
rm -r loc/ model/ obs/ time/ taka_results.png taka.in
echo ""

# Create directories for storing input and output
echo "Create output directories..."
base_dir=.
mkdir -p ${base_dir}/model # NonLinLoc velocity grids
mkdir -p ${base_dir}/time  # NonLinLoc time grids
mkdir -p ${base_dir}/obs  # NonLinLoc input observations
mkdir -p ${base_dir}/loc # NonLinLoc output
echo ""

# Define location of target volcano, region of interest, and time of interest
# Global Volcanism Program: https://volcano.si.edu/volcano.cfm?vn=311090
vlat=51.873
vlon=-178.006
velev=1449

# Time Period:
# - February 13, 2023: 164 events
t1="2023-02-12"
t2="2023-02-13"

# Event search parameters
event_rad_km=50

## Events - USGS catalog FDSN
#event_api="https://earthquake.usgs.gov/fdsnws/event/1/"
#event_cmd="${event_api}query?format=quakeml&includearrivals&starttime=${t1}&endtime=${t2}&lat=${vlat}&lon=${vlon}&maxradiuskm=${event_rad_km}"

# Inventory - Earthscope inventory FDSN
# Target: https://service.iris.edu/fdsnws/station/1/query?format=xml&level=station&lat=45.12345&lon=-123.1234&maxradius=1.0
inventory_api="https://service.iris.edu/fdsnws/station/1/"
inventory_rad_deg=1.0
inventory_cmd="${inventory_api}query?format=xml&level=station&lat=${vlat}&lon=${vlon}&maxradius=${inventory_rad_deg}"

#echo "Downloading events from USGS catalog..."
#echo "Event URL: ${event_cmd}"
#curl -o "${base_dir}/obs/events.xml" "${event_cmd}"
#echo ""

echo "Downloading events from USGS catalog with nllpy utility"
nllpy getfdsnevents --lat ${vlat} --lon ${vlon} --radiuskm ${event_rad_km} \
	--start ${t1} --end ${t2} \
	--client "USGS" \
	--output ${base_dir}/obs/events.xml
echo ""

echo "Converting QuakeML files to NLL_OBS"
nllpy quakeml2obs "${base_dir}/obs/events.xml" --output-dir "./obs"
echo ""

echo "Downloading station inventory..."
echo "Inventory URL: ${inventory_cmd}"
curl -o "${base_dir}/obs/stations.xml" "${inventory_cmd}"
echo ""

echo "Creating NonLinLoc control file..."
nllpy control \
    --template volcano \
    --lat ${vlat} \
    --lon ${vlon} \
    --elev ${velev} \
    --gridkm 100,100,1.0 \
    --depthkm 50,1.0 \
    --inventory "${base_dir}/obs/stations.xml" \
    --sta-fmt STA \
    --sig "Alaska Volcano Observatory" \
    --com "Takawangha earthquake swarm, February 12, 2023" \
    --prefix "taka" \
    --output "${base_dir}/taka.in"
echo "Control file created: ${base_dir}/taka.in"
echo ""

# Check if NonLinLoc is available
if ! command -v Vel2Grid &> /dev/null; then
    echo "Error: NonLinLoc not found. Please install NonLinLoc first."
    echo "Download from: http://alomax.free.fr/nlloc/"
    exit 1
fi

echo "Running NonLinLoc..."
echo "1. Vel2Grid..."
Vel2Grid "${base_dir}/taka.in"
echo ""

echo "2. Grid2Time..."
Grid2Time "${base_dir}/taka.in"
echo ""

#echo "3. NLLoc..."
NLLoc "${base_dir}/taka.in"
echo ""
echo "NonLinLoc processing complete!"
echo "Results available in: ${base_dir}/loc/"

# Optional: Plot results using ObsPy
echo "Creating basic plot of results..."
python taka_plot.py
