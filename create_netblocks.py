# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 12:36:04 2015

@author: Mutti
argument 1 country
argument 2 city
argument 3 location of maxmind csv files
"""

from netaddr import *
import sys
import os
import re


BASE_PATH = '/opt/masscan/targets/'


def grep(search_string, filename, options=''):
    '''
    Call OS grep
    Return matching lines
    '''
    result = ''
    p = os.popen("egrep " + options + ' "' + search_string + '" ' + filename, "r")
    while 1:
        line = p.readline()
        result += line
        if not line:
            break
    return result


def extract_cidr(csv_line):
    matchObj = re.match(r'(\d+\.\d+\.\d+\.\d+/\d+)', csv_line)
    if matchObj:
        return matchObj.group(1)


def write_log(output):
    datetime = time.strftime("%x") + ' ' + time.strftime("%X")
    with open(LOG_FILE, 'a') as f:
        f.write("%s: %s\n" % (datetime, output))


def write_city_netblock_to_file(netblock, filename):
    with open(BASE_PATH + filename, 'w+') as f:
        f.write(netblock)


def main():
    country = 'US'
    country = sys.argv[1]
    city = 'San Diego'
    city = sys.argv[2]
    maxmind_netblocks = '/opt/maxmind_geoip/processed/'
    maxmind_netblocks = sys.argv[3]
    grep_options = '-h'  # Don't print filenames
    grep_options += ' -r'  # Recursively search all files in directory
    result = grep(
        search_string=country+'.*'+city,
        filename=maxmind_netblocks,
        options=grep_options
        )
    # Seperate grep result into array
    cidr_blocks = [extract_cidr(csv_line) for csv_line in result.splitlines()]
    # Extract CIDR netblock
    merged_cidr_blocks = [IPNetwork(cidr_block) for cidr_block in cidr_blocks]
    print len(cidr_blocks)
    # Attempt to merge overlaping netblocks
    cidr_merge(merged_cidr_blocks)
    print len(merged_cidr_blocks)
    merged_cidr_blocks = [cidr.__str__() for cidr in merged_cidr_blocks]
    new_filename = country+"-"+city+".txt"
    write_city_netblock_to_file(
        '\n'.join(merged_cidr_blocks),
        new_filename.replace(" ", "_"),
        )
#        print cidr_blocks


if __name__ == '__main__':
    main()
