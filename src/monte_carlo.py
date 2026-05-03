import pandas as pd
import numpy as np
from fao56 import run_water_balance
from weather import get_weather_data



def adjust_weather(base_weather, temp_delta, rainfall_mult, wind_mult):
    """
    Apply Monte Carlo sampled variations to base weather data
    """
    df = base_weather.copy()
    
    df['temp_min']  += temp_delta
    df['temp_max']  += temp_delta
    df['rainfall']  *= rainfall_mult
    df['wind_speed'] *= wind_mult
    
    return df


def run_simulation(lat, lon, elevation=0, roof_height=0, n=10000):
    """
    Monte Carlo simulation of lettuce growing season viability
    n: number of simulations
    returns: dict of probabilistic results
    """
    # Pull base weather once
    base_weather = get_weather_data(lat, lon)
    growing_season = base_weather.iloc[90:165]  # April - June
    
    results = []
    
    for i in range(n):
        # Sample uncertain inputs
        temp_delta    = np.random.normal(0, 1.5)
        rainfall_mult = np.random.triangular(0.5, 1.0, 1.5)
        wind_mult     = np.random.uniform(0.8, 1.2)
        water_rate    = np.random.uniform(4.50, 8.00)
        
        # Adjust weather
        adjusted = adjust_weather(
            growing_season, temp_delta, rainfall_mult, wind_mult
        )
        
        # Run FAO-56 water balance
        balance = run_water_balance(
            adjusted, lat, elevation, roof_height
        )
        
        # Calculate irrigation cost
        farm_area_m2 = 100
        irrigation_liters = balance['total_irrigation_mm'] * farm_area_m2
        irrigation_hcf = irrigation_liters / 28316
        irrigation_cost = irrigation_hcf * water_rate
        
        results.append({
            'viable':           balance['viable'],
            'irrigation_mm':    balance['total_irrigation_mm'],
            'irrigation_cost':  irrigation_cost,
            'yield_reduction':  balance['yield_reduction_pct'],
            'avg_Ks':          balance['avg_Ks']
        })
    
    return summarize(results)


def summarize(results):
    """
    Aggregate 10,000 simulation results into probabilities
    """
    df = pd.DataFrame(results)
    
    return {
        'p_viable':            round(df['viable'].mean(), 4),
        'avg_irrigation_mm':   round(df['irrigation_mm'].mean(), 1),
        'avg_irrigation_cost': round(df['irrigation_cost'].mean(), 2),
        'cost_p05':            round(df['irrigation_cost'].quantile(0.05), 2),
        'cost_p95':            round(df['irrigation_cost'].quantile(0.95), 2),
        'avg_yield_reduction': round(df['yield_reduction'].mean(), 2),
        'yield_stability':     round(1 - df['yield_reduction'].std() / 100, 4)
    }



if __name__ == "__main__":
    print("Running Monte Carlo simulation...")
    print("(this may take 30-60 seconds)")
    
    results = run_simulation(
        lat=32.715,
        lon=-117.144,
        elevation=0,
        roof_height=0,
        n=10000
    )
    