# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 23:42:31 2015

@author: mkocbayi
"""
class GeoCityNetblockRecord:
    def __init__(
        self,
        network='',
        geoname_id='',
        registered_country_geoname_id='',
        represented_country_geoname_id='',
        is_anonymous_proxy='',
        is_satellite_provider='',
        postal_code='',
        latitude='',
        longitude='',
    ):
        self.network = network
        self.geoname_id = geoname_id
        self.registered_country_geoname_id = registered_country_geoname_id
        self.represented_country_geoname_id = represented_country_geoname_id
        self.is_anonymous_proxy = is_anonymous_proxy
        self.is_satellite_provider = is_satellite_provider
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
