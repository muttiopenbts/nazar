# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 23:50:33 2015

@author: mkocbayi
"""

class GeoCityLocationRecord:
    def __init__(
        self,
        geoname_id='',
        locale_code='',
        continent_code='',
        continent_name='',
        country_iso_code='',
        country_name='',
        subdivision_1_iso_code='',
        subdivision_1_name='',
        subdivision_2_iso_code='',
        subdivision_2_name='',
        city_name='',
        metro_code='',
        time_zone='',
    ):
        self.geoname_id = geoname_id
        self.locale_code = locale_code
        self.continent_code = continent_code
        self.continent_name = continent_name
        self.country_iso_code = country_iso_code
        self.country_name = country_name
        self.subdivision_1_iso_code = subdivision_1_iso_code
        self.subdivision_1_name = subdivision_1_name
        self.subdivision_2_iso_code = subdivision_2_iso_code
        self.subdivision_2_name = subdivision_2_name
        self.city_name = city_name
        self.metro_code = metro_code
        self.time_zone = time_zone
