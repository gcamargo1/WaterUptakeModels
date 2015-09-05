'''Module to create soil classes for each water uptake simulation module'''
#!/usr/bin/env python
from __future__ import division
import numpy as np
from functions import (bulk_density, sat_water_content,
                       vol_water_content_33_j_kg, vol_water_content_1500_jkg,
                       b_value, air_entry_pot, water_potential, water_content,
                       organic_m)

class Soil(object):
    """create a soil instance"""
    def __init__(self, book):
        CARBON_IN_OM = 0.58 #kgC/kgOM
        M2_TO_HECTARE = 10000 #m2/ha
        MG_TO_KG = 1000
        FIELD_CAPACITY_WP = -33 # J/kg
        PERMNT_WILT_POINT_WP = -1500 # J/kg
        self.WATER_DENSITY = 1000 #kg/m3
        sheet_soil = book.sheet_by_name('soil')
        self.total_layers = int(sheet_soil.cell(4, 2).value)
        self.layers = range(self.total_layers)
        self.daily_ref_evap_transp = int(sheet_soil.cell(5, 2).value)
        self.manual_organic_matter = sheet_soil.cell(5, 5).value
        self.manual_bulk_density = sheet_soil.cell(5, 6).value
        self.manual_field_capacity = sheet_soil.cell(5, 7).value
        self.manual_permanent_wilt_point = sheet_soil.cell(5, 8).value
        # Arrays declaration
        self.layer_thickness = np.zeros(self.total_layers)
        self.cum_depth = np.zeros(self.total_layers)
        self.clay = np.zeros(self.total_layers)
        self.sand = np.zeros(self.total_layers)
        self.organic_matter = np.zeros(self.total_layers)
        self.bulk_density = np.zeros(self.total_layers) # Mg/m3
        self.field_capacity = np.zeros(self.total_layers) # m3/m3
        self.mean_field_capacity = 0
        self.perm_wilt_point = np.zeros(self.total_layers) # m3/m3
        self.porosity = np.zeros(self.total_layers) # m3/m3
        self.b_value = np.zeros(self.total_layers)
        self.kl = np.zeros(self.total_layers) # cm2 / day
        self.air_entry_potential = np.zeros(self.total_layers)
        self.field_capacity_water_potential = np.zeros(self.total_layers)
        self.plant_avail_water = np.zeros(self.total_layers)
        self.init_plant_avail_water = np.zeros(self.total_layers)
        self.water_content = np.zeros(self.total_layers)
        self.init_water_avail = np.zeros(self.total_layers)
        self.water_potential = np.zeros(self.total_layers)
        self.perm_wilt_point_pot = np.zeros(self.total_layers)
        self.sat_water_potential = np.zeros(self.total_layers)

        for lyr in self.layers:
            self.layer_thickness[lyr] = sheet_soil.cell(9+lyr, 1).value
            self.cum_depth[lyr] = sheet_soil.cell(9+lyr, 2).value
            self.clay[lyr] = sheet_soil.cell(9+lyr, 3).value / 100
            self.sand[lyr] = sheet_soil.cell(9+lyr, 4).value / 100
            if self.manual_organic_matter:
                self.organic_matter[lyr] = sheet_soil.cell(9+lyr, 5).value
            else:
                self.organic_matter[lyr] = organic_m(self.clay[lyr])
            if self.manual_bulk_density:
                self.bulk_density[lyr] = sheet_soil.cell(9+lyr, 6).value
            else:
                self.bulk_density[lyr] = bulk_density(self.clay[lyr],
                                                      self.sand[lyr],
                                                      self.organic_matter[lyr])
            self.porosity[lyr] = sat_water_content(self.bulk_density[lyr])
            if self.manual_field_capacity:
                self.field_capacity[lyr] = sheet_soil.cell(9+lyr, 7).value
            else:
                self.field_capacity[lyr] = vol_water_content_33_j_kg(
                    self.clay[lyr], self.sand[lyr], self.organic_matter[lyr])
            if self.manual_permanent_wilt_point:
                self.perm_wilt_point[lyr] = sheet_soil.cell(9+lyr, 8).value
            else:
                self.perm_wilt_point[lyr] = vol_water_content_1500_jkg(
                    self.clay[lyr], self.sand[lyr], self.organic_matter[lyr])
            self.b_value[lyr] = b_value(self.field_capacity[lyr],
                                        self.perm_wilt_point[lyr])
            self.kl[lyr] = sheet_soil.cell(9+lyr, 11).value
            self.air_entry_potential[lyr] = air_entry_pot(
                self.field_capacity[lyr], self.porosity[lyr], self.b_value[lyr])
            if self.manual_field_capacity:
                self.field_capacity_water_potential[lyr] = water_potential(
                    self.porosity[lyr], self.air_entry_potential[lyr],
                    self.b_value[lyr], self.field_capacity[lyr])
            else:
                self.field_capacity_water_potential[lyr] = (
                    -0.35088 * self.clay[lyr] * 100 - 28.947) # needs ref
                # calculated again using more accurate formula
                self.field_capacity[lyr] = water_content(
                    self.porosity[lyr], self.air_entry_potential[lyr],
                    self.b_value[lyr], self.field_capacity_water_potential[lyr])
            if not self.manual_permanent_wilt_point:
                # calculated again using more accurate formula
                self.perm_wilt_point[lyr] = water_content(
                    self.porosity[lyr], self.air_entry_potential[lyr],
                    self.b_value[lyr], PERMNT_WILT_POINT_WP)
            assert self.perm_wilt_point[lyr] < self.field_capacity[lyr],\
             "Permanent wilting point must be less than field capacity"
            self.plant_avail_water[lyr] = (self.field_capacity[lyr]
                                           - self.perm_wilt_point[lyr])
            self.init_plant_avail_water[lyr] = sheet_soil.cell(9+lyr, 12).value
            self.water_content[lyr] = (self.init_plant_avail_water[lyr] *
                                       self.plant_avail_water[lyr] +
                                       self.perm_wilt_point[lyr])
            self.init_water_avail[lyr] = ((self.water_content[lyr] -
                                           self.perm_wilt_point[lyr]) *
                                          self.layer_thickness[lyr] *
                                          self.WATER_DENSITY)
            self.water_potential[lyr] = water_potential(
                self.porosity[lyr], self.air_entry_potential[lyr],
                self.b_value[lyr], self.water_content[lyr])
            self.perm_wilt_point_pot[lyr] = water_potential(
                self.porosity[lyr], self.air_entry_potential[lyr],
                self.b_value[lyr], self.perm_wilt_point[lyr])
            self.sat_water_potential[lyr] = water_potential(
                self.porosity[lyr], self.air_entry_potential[lyr],
                self.b_value[lyr], self.porosity[lyr])

        for lyr in self.layers:
            self.mean_field_capacity += (self.field_capacity[lyr] *
                                         self.layer_thickness[lyr])
        self.mean_field_capacity = (self.mean_field_capacity /
                                    self.layer_thickness.sum())

    def update_water_content(self, crop_list):
        """ updates soil water content based on each crop water uptake """
        for crop in crop_list:
            if True:#crop.planted_flag:
                for lyr in self.layers:
                    self.water_content[lyr] = (
                        self.water_content[lyr] - crop.water_uptake[lyr] /
                        (self.layer_thickness[lyr] * self.WATER_DENSITY))
                    self.water_potential[lyr] = (
                        water_potential(
                            self.porosity[lyr], self.air_entry_potential[lyr],
                            self.b_value[lyr], self.water_content[lyr]))
