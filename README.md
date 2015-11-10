Intro
nazar is a set of helper scripts to automate the use of masscan and reporting using ELK.

Requirments
GEO IP
masscan binary
ELK installation

Step 1
Download GEO IP data from Maxmind http://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip as city locations.
CSV format http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/GeoLiteCity-latest.zip
Save the csv files to /opt/maxmind_geoip
Should be two files, one contains location ids and the other actual netblocks.
Save extracted files to /opt/maxmind_geoip/
e.g. /opt/maxmind_geoip/GeoLite2-City-Blocks-IPv4.csv

Step 2
Run maxmind-geoip.py to join netblocks with city names using location IDs netblock ->location id <- city name.
This script will try to match the specified city with all location ids in the /opt/maxmind_geoip/GeoLite2-City-Locations-en.csv file and join with netblock csv. Result gets stored into processed directory as merged csv entry.
First argument tells mode csv or elastic, second argument for location of geo csv files from stage 1.
e.g. sudo ./maxmind-geoip.py csv '/opt/maxmind_geoip'
or sudo ./maxmind-geoip.py elastic '/opt/maxmind_geoip'

Step 3
Search processed maxmind csv files for netblocks relating to your city of interest.
e.g. python ./create_netblocks 'US' 'San Diego' '/opt/maxmind_geoip/processed'
result will be saved to /opt/masscan/targets/US-San Diego.txt

Step 4
Start scanning using masstive.py and file containing netblocks from step 3.
e.g. ./masstive.py /opt/masscan/targets/Netherlands-Schiphol.txt
Scan results are saved into files as scan-result-<country>-<city>-<start_block>-<end_block>.txt
under /opt/masscan/scan_results/processed/
User must specify file containing netblock from step 3 to scan.
Has ability to continue scanning from middle of netblock file by specifying which network line to continue from.

Step 5
Format scan results into correct style ready for database import.
Run data-import.py
Processed files are moved to /opt/masscan/scan_results/processed with new file names reflecting location.
Single csv file created per scanned country/city and created in /opt/nazar_feeds/masscan
Processed file also gets imported into elastic search database??
