'''
This script will format masscan results from file ready for import
into elastic search db
'''
import os
from os import path
import re
import datetime
from ScanRecord import ScanRecord
import time
from elasticsearch import Elasticsearch


BASE_PATH = '/opt/masscan/scan_results'
UNPROCESSED_DIRECTORY = BASE_PATH
PROCESSED_DIRECTORY = BASE_PATH + '/processed'
CSV_PATH = '/opt/nazar_feeds/masscan/'
LOG_FILE = '/tmp/nazar-log.txt'


def write_log(output):
    datetime = time.strftime("%x") + ' ' + time.strftime("%X")
    with open(LOG_FILE, 'a+') as f:
        f.write("%s: %s\n" % (datetime, output))


def get_fields_from_masscan_output(scan_result_record):
    # masscan simple port open output. Each open port is listed once.
    ip_address_search = re.search('Host: (.*?) .*?Ports: (\d+)/(.*?)/(.*?)/',
                                  scan_result_record, )
    if ip_address_search:
        scan_record = ScanRecord(
            ipAddress=ip_address_search.group(1),
            port=ip_address_search.group(2),
            state=ip_address_search.group(3),
            proto=ip_address_search.group(4),
            )
        return scan_record
    else:
        # This out format from masscan has banner information and multiple lines will have same ip, port.
        ip_address_search = re.search('Host: (.*?) .*?Port: (\d+).*?Service: (.*?)\sBanner: (.*)',
                                      scan_result_record, )
        if ip_address_search:
            scan_record = ScanRecord(
                ipAddress=ip_address_search.group(1),
                port=ip_address_search.group(2),
                service=ip_address_search.group(3),
                banner=ip_address_search.group(4),
                )
            return scan_record


def read_masscan_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            scan_record = get_fields_from_masscan_output(line)
            if scan_record is not None:
                yield scan_record


def save_db_record(scan_record, country, city, timestamp, es):
    es.index(
        index='scan',
        doc_type='masscan',
        id=None,
        body={
            'ip_address': scan_record.ipAddress,
            'port': scan_record.port,
            'state': scan_record.state,
            'proto': scan_record.proto,
            'service': scan_record.service,
            'banner': scan_record.banner,
            'country': country,
            'city': city,
            'timestamp': timestamp,
        }
    )


def get_country_from_file(filename):
    # Expect file name to look like this scan-result-US-SAN_DIEGO-107.222.124.0-107.222.127.255.txt
    country_search = re.search('scan-result-(.*?)-', filename, )
    if country_search:
        return country_search.group(1)


def get_city_from_file(filename):
    # Expect file name to look like this scan-result-US-SAN_DIEGO-107.222.124.0-107.222.127.255.txt
    city_search = re.search('scan-result-(.*?)-(.*?)-', filename, )
    if city_search:
        return city_search.group(2)


def get_timestamp_from_file(filename):
    return time.strftime('%Y-%m-%d-%H',
                         time.gmtime(os.path.getmtime(filename)))


def set_csv(scan_record, country, city, timestamp, csv_filename):
    # Create csv or append
    import csv
    with open(csv_filename, 'a') as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            dialect='excel',
            )
        line = [
            scan_record.ipAddress,
            scan_record.port,
            scan_record.state,
            scan_record.proto,
            scan_record.service,
            scan_record.banner,
            country,
            city,
            timestamp,
            ]
        csvwriter.writerow(line)


def main():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    write_log('Starting data import')
    # Check directory exists
    if os.path.isdir(PROCESSED_DIRECTORY):
        # Gather names of unprocessed scan result files
        list_of_scan_results = [f for f in os.listdir(UNPROCESSED_DIRECTORY) if path.isfile(UNPROCESSED_DIRECTORY+'/'+ f)]

        # Read each scan result file
        for scan_result_file in list_of_scan_results:
            write_log('Processing scan result file %s' % scan_result_file)
            unprocessed_fille = UNPROCESSED_DIRECTORY+'/'+scan_result_file
            records = read_masscan_file(unprocessed_fille)
            country = get_country_from_file(scan_result_file)
            city = get_city_from_file(scan_result_file)
            timestamp = get_timestamp_from_file(UNPROCESSED_DIRECTORY+'/'+scan_result_file)

            for record in records:
                set_csv(record, country, city, timestamp, CSV_PATH+timestamp+".txt")
                # Save record into elastic search db
                save_db_record(record, country, city, timestamp, es)
                print "Saved record to Elasticsearch db"
            # Move scan result file to processed directory
            os.rename(unprocessed_fille, PROCESSED_DIRECTORY+'/'+scan_result_file)
    else:
        print PROCESSED_DIRECTORY + " doesn't exist"
    write_log('Ending data import')

if __name__ == '__main__':
    main()
