#!/usr/bin/python
'''
TODO: make code more efficient by slurping location id from location file and parsing netblock
file once.
Argument 1 mode, elastic|csv
Argument 2 path of maxmind csv files
'''
from tempfile import NamedTemporaryFile
from GeoCityLocationRecord import GeoCityLocationRecord
from GeoCityNetblockRecord import GeoCityNetblockRecord
import shutil
import csv
import re
import time
import os
import sys
from elasticsearch import Elasticsearch
import json
import requests


BASE_URL = '/opt/maxmind_geoip/'
BASE_URL = sys.argv[2]
NEW_GEOIP_PATH = BASE_URL+'processed/'
GEO_LOCATION_FILE = BASE_URL + 'GeoLite2-City-Locations-en.csv'
GEO_NETBLOCK_FILE = BASE_URL+'GeoLite2-City-Blocks-IPv4.csv'
TEMP_GEO_NETBLOCK_FILE = NamedTemporaryFile(delete=False)
TEMP_FILENAME = NamedTemporaryFile(delete=False)
LOG_FILE = '/tmp/maxmind-log.txt'


def write_log(output):
    datetime = time.strftime("%x") + ' ' + time.strftime("%X")
    with open(LOG_FILE, 'a+') as f:
        f.write("%s: %s\n" % (datetime, output))


# Yield line of geo from csv
def get_line_from_csv(filename):
    with open(filename, 'rb') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')

        for row in reader:
            yield row


def set_csv_row(filename, location_row, new_data_array):
    writer = csv.writer(filename, delimiter=',', quotechar='"')

    for row in new_data_array:
        # remove duplicate fields
        writer.writerow(row+location_row)


def get_all_matching_locationid_from_netblock_file(csv_line):
    '''
    Find all rows that match location id and shrink the csv by deleting
    matching rows
    '''
    matching_rows = []
    location_id = get_locationid_from_location_file(csv_line)

    for row in get_line_from_csv(GEO_NETBLOCK_FILE):
        location_id_from_netblock = get_locationid_from_netblock_file(row)
        if location_id == location_id_from_netblock:
            matching_rows.append(row)
    return matching_rows


def get_locationid_from_netblock_file(csv_line):
    # field 2 should be geoname_id
    return csv_line[1]


def get_locationid_from_location_file(csv_line):
    # field 1 should be geoname_id
    return csv_line[0]


def bi_contains(lst, item):
    from bisect import bisect_left
    """ efficient `item in lst` for sorted lists """
    # if item is larger than the last its not in the list, but the bisect would
    # find `len(lst)` as the index to insert, so check that first. Else, if the
    # item is in the list then it has to be at index bisect_left(lst, item)
    return (item <= lst[-1]) and (lst[bisect_left(lst, item)] == item)


def grep(search_string, filename):
    '''
    Call OS grep
    Return matching lines
    '''
    result = ''
    p = os.popen("egrep " + search_string + " " + filename, "r")
    while 1:
        line = p.readline()
        result += line
        if not line:
            break
    return result


def convertCsvRowToList(list_lines):
    csv_lines = []
    for row in list_lines:
        csv_lines.append(row.split(','))
    return csv_lines


def processUsingGrep():
    write_log("Starting maxmind geo IP netblock processing")
    location_csv_file = get_line_from_csv(GEO_LOCATION_FILE)
    location_csv_file.next()  # skip csv header

    for location_line in location_csv_file:
        location_id_from_location = \
            get_locationid_from_location_file(location_line)
        location_id_regex = \
            '"^([0-9]+\.){,3}[0-9]+\/[0-9]+,' + \
            location_id_from_location + \
            ',"'  # Helps speed up grep re search
        grep_result = grep(location_id_regex, GEO_NETBLOCK_FILE)
        netblock_lines = grep_result.splitlines()
        if netblock_lines:
            TEMP_GEO_NETBLOCK_FILE = NamedTemporaryFile(delete=False)
            # Convert result of grep string to csv arrays
            netblock_lines = convertCsvRowToList(netblock_lines)
            location_line.pop(0)
            set_csv_row(TEMP_GEO_NETBLOCK_FILE, location_line, netblock_lines)
            # Create new csv file for each city
            new_city_cvs_filename = location_id_from_location + '.csv'
            log_message = 'Writing new csv file %s' % \
                (new_city_cvs_filename)
            write_log(log_message)
            shutil.move(TEMP_GEO_NETBLOCK_FILE.name,
                        NEW_GEOIP_PATH + new_city_cvs_filename)
    write_log("End maxmind geo IP netblock processing")


def processUsingCsvMem():
    # run through location file and save location ids in mem
    location_file_rows = []
    for location_line in get_line_from_csv(GEO_LOCATION_FILE):
        location_file_rows.append(location_line)
    # get csv generator and skip header
    geo_netblock_csv = get_line_from_csv(GEO_NETBLOCK_FILE)
    geo_netblock_csv.next()
    # Iterate through netblock lines in csv
    for netblock_line in geo_netblock_csv:
        # Find matching location id in memory
        for location_row in location_file_rows:
            location_id_from_location = \
                get_locationid_from_location_file(location_row)
            location_id_from_netblock = \
                get_locationid_from_netblock_file(netblock_line)
            # we have a match? Save to temp csv
            if location_id_from_location == location_id_from_netblock:
                # remove duplicate field from row
                location_row.pop(0)
                set_csv_row(TEMP_GEO_NETBLOCK_FILE,
                            location_row, [netblock_line])
                # print location_id_from_location
                # print location_id_from_netblock
                # found a match, stop break loop
                break
    shutil.move(TEMP_GEO_NETBLOCK_FILE.name, NEW_GEOIP_FILENAME)


def csvMode():
    if not os.path.exists(NEW_GEOIP_PATH):
        os.makedirs(NEW_GEOIP_PATH)
    processUsingGrep()


def save_netblock_record(
    network,
    geoname_id,
    registered_country_geoname_id,
    represented_country_geoname_id,
    is_anonymous_proxy,
    is_satellite_provider,
    postal_code,
    latitude,
    longitude,
    es,
        ):
    es.index(
        index='geo_city_netblock',
        doc_type='maxmind',
        id=None,
        body={
            'network': network,
            'geoname_id': geoname_id,
            'registered_country_geoname_id': registered_country_geoname_id,
            'represented_country_geoname_id': represented_country_geoname_id,
            'is_anonymous_proxy': is_anonymous_proxy,
            'is_satellite_provider': is_satellite_provider,
            'postal_code': postal_code,
            'location': latitude + ',' + longitude,
        }
    )


def save_location_record(
        geoname_id,
        locale_code,
        continent_code,
        continent_name,
        country_iso_code,
        country_name,
        subdivision_1_iso_code,
        subdivision_1_name,
        subdivision_2_iso_code,
        subdivision_2_name,
        city_name,
        metro_code,
        time_zone,
        es):
    es.index(
        index='geo_city_location',
        doc_type='maxmind',
        id=None,
        body={
            'geoname_id': geoname_id,
            'locale_code': locale_code,
            'continent_code': continent_code,
            'continent_name': continent_name,
            'country_iso_code': country_iso_code,
            'country_name': country_name,
            'subdivision_1_iso_code': subdivision_1_iso_code,
            'subdivision_1_name': subdivision_1_name,
            'subdivision_2_iso_code': subdivision_2_iso_code,
            'subdivision_2_name': subdivision_2_name,
            'city_name': city_name,
            'metro_code': metro_code,
            'time_zone': time_zone,
        }
    )


def prepareEsIndexes():
    # netblock index
    payload = {
       "geo_city_netblock": {
                "properties": {
                   "geoname_id": {
                      "type": "string"
                   },
                   "is_anonymous_proxy": {
                      "type": "string"
                   },
                   "is_satellite_provider": {
                      "type": "string"
                   },
                   "location": {
                            "type": "geo_point",
                            "geohash": "false",
                   },
                   "network": {
                      "type": "string"
                   },
                   "postal_code": {
                      "type": "string"
                   },
                   "registered_country_geoname_id": {
                      "type": "string"
                   },
                   "represented_country_geoname_id": {
                      "type": "string"
                   }
                }
           }
    }

    payload_json = json.dumps(payload)
    #  Delete index if exists
    requests.delete("http://localhost:9200/geo_city_netblock/")
    #  Create index
    requests.put("http://localhost:9200/geo_city_netblock/")
    #  Set index mapping
    requests.put("http://localhost:9200/geo_city_netblock/geo_city_netblock/_mapping", data=payload_json)

    # location index
    #  Delete index if exists
    requests.delete("http://localhost:9200/geo_city_location/")


def elasticsearchMode():
    prepareEsIndexes()
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    write_log("Starting maxmind geo IP location processing with elasticsearch db")
    location_csv_file = get_line_from_csv(GEO_LOCATION_FILE)
    location_csv_file.next()  # skip csv header
    for location_line in location_csv_file:
        location_line.append(es)
        save_location_record(*location_line)
    write_log("End maxmind geo IP location processing")

    write_log("Starting maxmind geo IP netblock processing with elasticsearch db")
    netblock_csv_file = get_line_from_csv(GEO_NETBLOCK_FILE)
    netblock_csv_file.next()  # skip csv header
    for netblock_line in netblock_csv_file:
        netblock_line.append(es)
        save_netblock_record(*netblock_line)
    write_log("End maxmind geo IP netblock processing")


def main(argv):
    if argv[1] == 'elastic':
        elasticsearchMode()
    else:
        csvMode()


if __name__ == '__main__':
    main(sys.argv)
