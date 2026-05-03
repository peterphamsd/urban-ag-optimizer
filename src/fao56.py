import numpy as np
import pandas as pd

def sat_vapour_pressure(T):
    """
    saturation vapour pressure at temperature T
    FAO-56 Equation 11
    T: temperature in Celsius
    returns: pressure in kPa
    """
    return 0.6108 * np.exp(17.27 * T / (T + 237.3))


def mean_sat_vapour_pressure(Tmin, Tmax):
    """
    mean saturation vapour pressure for a day
    FAO-56 Equation 12
    returns: es in kPa
    """
    return (sat_vapour_pressure(Tmin) + sat_vapour_pressure(Tmax)) / 2


def actual_vapour_pressure(Tmin, humidity):
    """
    actual vapour pressure from relative humidity and Tmin
    FAO-56 Equation 48
    humidity: relative humidity in %
    returns: ea in kPa
    """
    return sat_vapour_pressure(Tmin) * (humidity / 100)

def slope_vapour_pressure(T):
    """
    Slope of saturation vapour pressure curve
    FAO-56 Equation 13
    T: mean daily temperature in Celsius
    returns: delta in kPa/°C
    """
    return (4098 * sat_vapour_pressure(T)) / (T + 237.3) ** 2


def psychrometric_constant(elevation):
    """
    Psychrometric constant
    FAO-56 Equation 8
    elevation: meters above sea level
    returns: gamma in kPa/°C
    """
    # Atmospheric pressure at elevation
    P = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26
    
    # Psychrometric constant
    return 0.000665 * P



def net_shortwave_radiation(Rs, albedo=0.23):
    """
    Net shortwave radiation
    FAO-56 Equation 38
    Rs: incoming solar radiation MJ/m2/day
    albedo: reflection coefficient (0.23 for reference grass)
    returns: Rns in MJ/m2/day
    """
    return (1 - albedo) * Rs


def net_longwave_radiation(Tmin, Tmax, Rs, Rso, ea):
    """
    Net longwave radiation
    FAO-56 Equation 39
    Tmin, Tmax: min/max temperature in Celsius
    Rs: actual solar radiation MJ/m2/day
    Rso: clear sky solar radiation MJ/m2/day
    ea: actual vapour pressure kPa
    returns: Rnl in MJ/m2/day
    """
    # Convert to Kelvin
    TminK = Tmin + 273.16
    TmaxK = Tmax + 273.16
    
    # Stefan-Boltzmann constant
    sigma = 4.903e-9
    
    # Cloudiness factor
    cloudiness = (0.34 - 0.14 * np.sqrt(ea))
    
    # Relative shortwave radiation (capped at 1.0)
    Rs_Rso = min(Rs / Rso, 1.0)
    radiation_ratio = 1.35 * Rs_Rso - 0.35
    
    # Temperature term
    temp_term = sigma * (TmaxK**4 + TminK**4) / 2
    
    return temp_term * cloudiness * radiation_ratio


def net_radiation(Rns, Rnl):
    """
    Net radiation at crop surface
    FAO-56 Equation 40
    returns: Rn in MJ/m2/day
    """
    return Rns - Rnl

def clear_sky_radiation(Ra, elevation):
    """
    Clear sky solar radiation
    FAO-56 Equation 37
    Ra: extraterrestrial radiation MJ/m2/day
    elevation: meters above sea level
    returns: Rso in MJ/m2/day
    """
    return (0.75 + 2e-5 * elevation) * Ra


def extraterrestrial_radiation(lat, day_of_year):
    """
    Extraterrestrial radiation
    FAO-56 Equation 21
    lat: latitude in degrees
    day_of_year: Julian day (1-365)
    returns: Ra in MJ/m2/day
    """
    # Convert latitude to radians
    phi = np.radians(lat)
    
    # Inverse relative distance Earth-Sun
    dr = 1 + 0.033 * np.cos(2 * np.pi * day_of_year / 365)
    
    # Solar declination
    delta = 0.409 * np.sin(2 * np.pi * day_of_year / 365 - 1.39)
    
    # Sunset hour angle
    omega_s = np.arccos(-np.tan(phi) * np.tan(delta))
    
    # Solar constant
    Gsc = 0.0820
    
    Ra = (24 * 60 / np.pi) * Gsc * dr * (
        omega_s * np.sin(phi) * np.sin(delta) +
        np.cos(phi) * np.cos(delta) * np.sin(omega_s)
    )
    
    return Ra

def soil_heat_flux():
    """
    Soil heat flux for daily timestep
    FAO-56 Equation 42
    For daily periods, G is small and assumed = 0
    """
    return 0


def adjust_wind_speed(uz, z):
    """
    Adjust wind speed from measurement height to 2m equivalent
    FAO-56 Equation 47
    uz: wind speed at height z (m/s)
    z: measurement height in meters
    returns: u2 in m/s
    """
    if z == 2:
        return uz
    return uz * (4.87 / np.log(67.8 * z - 5.42))



def compute_ETo(Tmin, Tmax, solar_rad, wind_speed, humidity, 
                lat, day_of_year, elevation=0, roof_height=0):
    """
    Penman-Monteith Reference Evapotranspiration
    FAO-56 Equation 6
    returns: ETo in mm/day
    """
    Tmean = (Tmin + Tmax) / 2
    
    # Adjust wind for rooftop if needed
    if roof_height > 2:
        u2 = adjust_wind_speed(wind_speed, roof_height)
    else:
        u2 = adjust_wind_speed(wind_speed, 2)
    
    # Vapour pressure
    es = mean_sat_vapour_pressure(Tmin, Tmax)
    ea = actual_vapour_pressure(Tmin, humidity)
    
    # Slope and psychrometric constant
    delta = slope_vapour_pressure(Tmean)
    gamma = psychrometric_constant(elevation)
    
    # Radiation
    Ra = extraterrestrial_radiation(lat, day_of_year)
    Rso = clear_sky_radiation(Ra, elevation)
    Rns = net_shortwave_radiation(solar_rad)
    Rnl = net_longwave_radiation(Tmin, Tmax, solar_rad, Rso, ea)
    Rn = net_radiation(Rns, Rnl)
    G = soil_heat_flux()
    
    # Penman-Monteith
    numerator = (0.408 * delta * (Rn - G) + 
                 gamma * (900 / (Tmean + 273)) * u2 * (es - ea))
    denominator = delta + gamma * (1 + 0.34 * u2)
    
    return numerator / denominator



def get_kc(day):
    """
    Crop coefficient for lettuce by day of growing season
    FAO-56 Table 12 values for lettuce
    day: day of growing season (1-75)
    returns: Kc value
    """

    #number of days for each state
    L_ini = 20
    L_dev = 30
    L_mid = 15
    L_late = 10

    end_ini = L_ini
    end_dev = L_ini + L_dev
    end_mid = L_ini + L_dev + L_mid
    end_late = L_ini + L_dev + L_mid + L_late

    Kc_ini = 0.70
    Kc_mid = 1.00
    Kc_end = 0.95

    if day <= end_ini:
        # initial stage — flat
        return Kc_ini

    elif day <= end_dev:
        # development stage — interpolate from Kc_ini to Kc_mid
        progress = (day - end_ini) / L_dev
        return (0.7 + (1.00 - 0.7) * progress)

    elif day <= end_mid:
        # mid-season — flat
        return Kc_mid

    elif day <= end_late:
        # late season — interpolate from Kc_mid to Kc_end
        progress = (day - end_mid) / L_late
        return (Kc_mid + (Kc_end - Kc_mid) * progress)

    else:
        # season over
        return 0



for day in [1, 20, 25, 35, 50, 55, 65, 70, 75]:
    print(f"Day {day:3d}: Kc = {get_kc(day):.4f}")
