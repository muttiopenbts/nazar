# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 20:14:54 2015

@author: mkocbayi
Script for kicking of masscan scans.
Argument 1 should be location of file containing cidr blocks
to scan. e.g. /opt/masscan/targets/US-San Diego.txt
10.0.0.0/24
"""
import csv
import re
import time
import os
import sys
from netaddr import *


LOG_FILE = '/tmp/masscan-log.txt'
# This is where scan results are expected to be saved before being saved to db
BASE_PATH = '/opt/masscan/scan_results/'
BASE_PATH = sys.argv[3]
MASSCAN_BINARY = '../masscan/bin/masscan'
MASSCAN_BINARY = sys.argv[2]
SCAN_RATE = 10000


def write_log(output):
    datetime = time.strftime("%x") + ' ' + time.strftime("%X")
    with open(LOG_FILE, 'a+') as f:
        f.write("%s: %s\n" % (datetime, output))


def run_cmd(cmd):
    '''
    Call OS cmd
    '''
    result = ''
    p = os.popen(cmd, "r")
    while 1:
        line = p.readline()
        result += line
        if not line:
            break
    return result


def get_country_from_file(filename):
    # Expect file name to look like this /path/US-SAN DIEGO.txt
    # Also convert spaces into underscore
    country_search = re.search('.*/(.*?)-(.*)$', filename, )
    if country_search:
        country = country_search.group(1)
        return country.replace(" ", "_")


def get_city_from_file(filename):
    # Expect file name to look like this /path/US-SAN DIEGO.txt
    # Also convert spaces into underscore
    city_search = re.search('.*/(.*?)-(.*?)\.txt$', filename, )
    if city_search:
        city = city_search.group(2)
        return city.replace(" ", "_")


def binary_exist(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def main():
    if not binary_exist(MASSCAN_BINARY):
        print "Please specify path and binary for masscan. Check readme for help."
        return
    if not os.path.isdir(BASE_PATH):
        print "Directory for storing scan results not specified or not exist."
        return
    target_cidr_blocks_file = sys.argv[1]
    country = get_country_from_file(target_cidr_blocks_file)
    city = get_city_from_file(target_cidr_blocks_file)
    # Open netblock file and read each entry into array
    cidr_blocks = [line.strip() for line in open(target_cidr_blocks_file, 'r')]

    for network in cidr_blocks:
        ip_network = IPNetwork(network)
        start_block = str(ip_network[0])
        end_block = str(ip_network[-1])
        #  Masscan banner grabbing needs a firewall rule to prevent connections being reset
        run_cmd('iptables -A INPUT -p tcp -i eth0 --dport 61234 -j DROP')
        results_file = BASE_PATH + 'scan-result-%s-%s-%s-%s.txt' % (country, city, start_block, end_block)
        masscan_cmd = '%s -p 80,443 %s --rate %s --banners --capture html --capture cert --retries 2 --adapter-port 61234 -oG %s' % (MASSCAN_BINARY, network, SCAN_RATE, results_file)
        write_log('Kicking off masstive scan for %s' % network)
        run_cmd(masscan_cmd)
        write_log('End masscan for %s' % network)


if __name__ == '__main__':
    main()
