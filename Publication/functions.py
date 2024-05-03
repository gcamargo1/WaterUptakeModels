""" Auxiliary functions from water uptake models for water uptake:
bulk_density
sat_water_content
vol_water_content_33_j_kg
vol_water_content_1500_jkg
b_value
air_entry_pot
water_potential
organic_m
feddes_stress_factor
p_wofost
"""
# -*- coding: utf-8 -*-
from __future__ import division
import math


def bulk_density(clay, sand, organic_matter):
    """(float, float,float) -> (float)

    Returns Bulk density (Mg/m3 or g/cm3)

    clay: clay content (fraction)
    sand: sand content (fraction)
    organic_matter: organic matter (%)

    Reference: Saxton, K.E., Rawls, W.J., 2006. Soil water characteristic
     estimates by texture and organic matter for hydrologic solutions. Eq. 5,6
     Soil Sci. Soc. Am. J. 70, 1569-1578.

    >>> bulk_density(0.03,0.92,1.906)
    1.43
    >>> bulk_density(0.15,0.2,2.29)
    1.39
    """
    MIN_SOIL_PARTICLE_DENS = 2.65
    x1 = (
        0.078
        + 0.278 * sand
        + 0.034 * clay
        + 0.022 * organic_matter
        - 0.018 * sand * organic_matter
        - 0.027 * clay * organic_matter
        - 0.584 * sand * clay
    )
    x2 = -0.107 + 1.636 * x1
    field_capacity = vol_water_content_33_j_kg(clay, sand, organic_matter)  # m3/m3
    sat_water_content = 0.043 + field_capacity + x2 - 0.097 * sand
    return (1 - sat_water_content) * MIN_SOIL_PARTICLE_DENS


def sat_water_content(bulk_density):
    """
    Returns the saturated water content (m3/m3)

    bulk_density: bulk density (Mg / m3)

    Reference: Campbell, G.S., 1985. Soil physics with BASIC: Transport models
     for soil-plant systems. Elsevier, Amsterdam.

     >>> sat_water_content(1.3)
    0.5094339622641508
    """
    MIN_SOIL_PARTICLE_DENS = 2.65  # Mg/m3
    return 1 - bulk_density / MIN_SOIL_PARTICLE_DENS


def vol_water_content_33_j_kg(clay, sand, organic_matter):
    """(float,float,float) -> (float)

    Returns the volumetric water content at field capacity (33 J/kg) (m3/m3)

    clay: clay content (fraction)
    sand: sand content (fraction)
    organic_matter: organic matter (%)

    Reference: Saxton, K.E., Rawls, W.J., 2006. Soil water characteristic
     estimates by texture and organic matter for hydrologic solutions.
     Soil Sci. Soc. Am. J. 70, 1569-1578. eq.2 R2=0.63

    >>> vol_water_content_33_j_kg (0.03,0.92,1.906)
    0.08
    >>> vol_water_content_33_j_kg (0.33,0.09,2.866)
    0.38
    """
    x1 = (
        0.299
        - 0.251 * sand
        + 0.195 * clay
        + 0.011 * organic_matter
        + 0.006 * sand * organic_matter
        - 0.027 * clay * organic_matter
        + 0.452 * sand * clay
    )
    return -0.015 + 0.636 * x1 + 1.283 * x1**2


def vol_water_content_1500_jkg(clay, sand, organic_matter):
    """(float,float,float) -> (float)

    Returns the volumetric water content at field capacity (33 J/kg) (m3/m3)

    clay: clay content (fraction)
    sand: sand content (fraction)
    organic_matter: organic matter (%)

    Reference: Saxton, K.E., Rawls, W.J., 2006. Soil water characteristic
     estimates by texture and organic matter for hydrologic solutions.
     Soil Sci. Soc. Am. J. 70, 1569-1578. eq.1 R2=0.86

    >>> vol_water_content_1500_jkg (0.03,0.92,1.906)
    0.03
    >>> vol_water_content_1500_jkg (0.33,0.09,2.866)
    0.21
    """
    x1 = (
        0.031
        - 0.024 * sand
        + 0.487 * clay
        + 0.006 * organic_matter
        + 0.005 * sand * organic_matter
        - 0.013 * clay * organic_matter
        + 0.068 * sand * clay
    )
    return -0.02 + 1.14 * x1


def b_value(water_content_33_j_kg, water_content_1500_j_kg):
    """(float,float) -> float

    Return b soil parameter

    water_content_33_j_kg: water content at -33 J/kg
    water_content_1500_j_kg: water content at -1500 J/kg

    Reference: Saxton, K.E., Rawls, W.J., 2006. Soil water characteristic
     estimates by texture and organic matter for hydrologic solutions. Soil Sci.
     Soc. Am. J. 70, 1569-1578.

    >>> b_value(0.08,0.03)
    3.89
    """
    return (math.log(1500) - math.log(33)) / (
        math.log(water_content_33_j_kg) - math.log(water_content_1500_j_kg)
    )


def air_entry_pot(field_capacity, sat_water_content, b_value):
    """(float,float,float) -> float

    Return air entry potential

    field_capacity: water content at field capacity
    sat_water_content: saturated water content
    b_value: soil parameter

    Reference: Kemanian, A.R., Stockle, C.O., 2010. C-Farm: A simple model to
    evaluate the carbon balance of soil profiles. Eur. J. Agron. 32, 22-29.
    >>> air_entry_pot(.08,0.5,4.33)
    -0.0118
    """
    return -33 * (field_capacity / sat_water_content) ** b_value


def water_potential(sat_water_content, air_entry_potential, campbell_b, water_content):
    """(float,float,float,float) -> (float)

    Returns Soil Water Potential (J/kg)

    sat_water_content : saturation water content (m3/m3)
    air_entry_potential: air entry water potential (J/kg)
    campbell_b: soil moisture release curve parameter
    water_content: water content (m3/m3)

    Reference: Campbell, G.S., 1985. Soil physics with BASIC: Transport models
     for soil-plant systems. Elsevier, Amsterdam. Eq. 5.9

    >>> water_potential (0.5, -1.5, 5, 0.25)
    -48.0
    >>> water_potential (0.20, -1.0, 4, 0.25)
    -0.4096"""
    assert sat_water_content > 0, "sat water content must be positive"
    assert water_content > 0, "water content must be positive"

    return air_entry_potential * (sat_water_content / water_content) ** campbell_b


def water_content(sat_water_content, air_entry_potential, campbell_b, water_potential):
    """(float,float,float) -> (float)

    Returns Soil water content (m3/m3)

    sat_water_content : saturation water content (m3/m3)
    air_entry_potential: air entry water potential (J/kg)
    campbell_b: soil moisture release curve parameter
    water_potential: matric water potential (J/kg)

    Reference: Campbell, G.S., 1985. Soil physics with BASIC: Transport models
     for soil-plant systems. Elsevier, Amsterdam. pp.80

    >>> water_content(0.5,-1.5,5,-52.7)
    0.24
    """
    return sat_water_content * (water_potential / air_entry_potential) ** (
        -1 / campbell_b
    )


def organic_m(clay):
    """(float) -> float
    Half of carbon saturation given by the original author, and converted to organic matter
    carbon = 0.58 * organic_matter

    clay: clay content (0-1)

    Hassink, J., and A. P. Whitmore. 1997. A Model of the Physical Protection of
     Organic Matter in Soils. Soil Sci. Soc. Am. J. 61(1):131-139.

    >>> organic_matter(0.5)
    3.41
    >>> organic_matter(0.03)
    1.91
    """
    return 1.81 + 0.032 * clay * 100


def feddes_stress_factor(
    transp_pot,
    water_pot,
    water_pot_sat,
    water_pot_field_cap,
    water_pot_stress_low_t,
    water_pot_stress_high_t,
    water_pot_wilting,
    transp_high,
    transp_low,
):
    """
    Reduction coefficient for root water uptake

    transp_pot: potential transpiration, mm/day
    water_pot: soil water potential, J/kg
    field_capacity_wp = field capacity water potential, J/kg
    water_pot_wilting = wilting point water potential, J/kg

    References:
    Feddes, R. A., P. J. Kowalik, and H. Zaradny. 1978. Simulation of field
     water use and crop yield. Wageningen.
    Simunek, J., T. Vogel, and M. T. v. Genuchten. 1994. The SWMS _ 2D Code for
     Simulating Water Flow and Solute Transport in Two-Dimensional Variably
     Saturated Media. FAlfa function
    """
    assert water_pot < 0, "water potential cannot be positive"
    if transp_pot < transp_low:
        water_pot_stress = water_pot_stress_low_t
    if transp_pot > transp_high:
        water_pot_stress = water_pot_stress_high_t
    if transp_pot >= transp_low and transp_pot <= transp_high:
        water_pot_stress = water_pot_stress_high_t + (transp_high - transp_pot) / (
            transp_high - transp_low
        ) * (water_pot_stress_low_t - water_pot_stress_high_t)
    # Stressed condition, reducing transpiration
    if water_pot > water_pot_wilting and water_pot < water_pot_stress:
        return (water_pot - water_pot_wilting) / (water_pot_stress - water_pot_wilting)
    # Optimal conditions
    if water_pot >= water_pot_stress and water_pot <= water_pot_field_cap:
        return 1.0
    # Saturated conditions (reducing T)
    if water_pot > water_pot_field_cap and water_pot < water_pot_sat:
        return (water_pot - water_pot_sat) / (water_pot_field_cap - water_pot_sat)
    # Beyond wilting water potential
    if water_pot <= water_pot_wilting:
        return 0
    # Beyond saturation water potential
    if water_pot >= water_pot_sat:
        return 0


def p_wofost(ET, drought_cat):
    """(float, int) -> float
    Calculates the soil water depletion factor (p) as a function of potential
    evapotranspiration based on different plants sensitivity to drought

    ET: evapotranspiration, mm/d
    drought_cat: crop drought category (1 (sensitive) to 5(resistant))

    Ref: Doorenbos, J., Kassam, A.H., Bentvelder, C., Uittenbogaard, G., 1978.
     Yield response to water. U.N. Economic Commission West Asia, Rome, Italy

     Diepen, C. A. van, C. Rappoldt, J. Wolf & H. van Keulen, 1988. Crop growth
      simulation model WOFOST. Documentation version 4.1, Centre for World Food
      Studies, Wageningen, The Netherlands. 299 pp.
    source file: sweaf.for

    >>> p_wofost(5, 4)
    0.5622516556291391
    >>> p_wofost(10, 4)
    0.34247787610619473
    """
    MM_TO_CM = 10.0
    ET = ET / MM_TO_CM
    A = 0.76
    B = 1.5
    stress_fact = 1.0 / (A + B * ET) - (5.0 - drought_cat) * 0.10
    if drought_cat < 3:
        stress_fact = stress_fact + (ET - 0.6) / (drought_cat * (drought_cat + 3.0))
    if stress_fact < 0.1:
        stress_fact = 0.1
    if stress_fact > 0.95:
        stress_fact = 0.95
    return stress_fact


def vapor_pressure_air(
    vapor_pressure_temp_min, vapor_pressure_temp_max, rh_max, rh_min
):
    """
    Return the vapor pressure of air (kPa)

    vapor_pressure_temp_min: saturated vapor pressure of min temperature (kPa)
    vapor_pressure_temp_max: saturated vapor pressure of max temperature (kPa)
    rh_max: max relative humidity (0 - 100)
    rh_min: min relative humidity (0 - 100)

    Reference: Campbell, G.S., Norman, J.M., 1998. Introduction to environmental
     biophysics. Springer, New York.

    >>> vapor_pressure_air(1.817,5.320,87,25)
    1.455
    """
    return 0.5 * (
        vapor_pressure_temp_min * rh_max / 100.0
        + vapor_pressure_temp_max * rh_min / 100.0
    )


def vapor_press_defct_ave(max_sat_vap_press, min_sat_vap_press, air_vap_press):
    """max_sat_vap_press: max sat vapor pressure - kPa
    min_sat_vap_press: min sat vapor pressure - kPa
    air_vap_press: air vapor pressure - kPa
    """
    return (max_sat_vap_press + min_sat_vap_press) / 2.0 - air_vap_press


def vapor_press_defct_max(max_sat_vap_press, min_relative_humidity):
    """max vapor presure deficit"""
    return 0.67 * max_sat_vap_press * (1 - min_relative_humidity / 100.0)
