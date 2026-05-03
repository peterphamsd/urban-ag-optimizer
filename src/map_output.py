import folium
import pandas as pd
import geopandas as gpd



def get_color(score):
    if score >= 80:
        return 'green'
    elif score >= 65:
        return 'orange'
    else:
        return 'red'
    

def build_map(ranked_df):
    #center the map on the specific location
    m = folium.Map(location = [32.7157, -117.1611], zoom_start=12, tiles='CartoDB positron')

    for _, row in ranked_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=10,
            color=get_color(row['score']),
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(f"""
                <b>{row['address']}</b><br>
                <hr>
                <b>Overall Score: {row['score']}</b><br>
                <br>
                <b>Water Viability (FAO-56 + Monte Carlo)</b><br>
                P(viable): {row['p_viable']*100:.0f}%<br>
                Avg irrigation cost: ${row['avg_cost']:.2f}/season per 100m²<br>
                Yield stability: {row['yield_stability']:.4f}<br>
                <br>
                <b>Site Characteristics</b><br>
                Land use: {row['land_use']}<br>
                Lot size: {row['lot_sqft']:,} sqft<br>
                Transit distance: {row['transit_distance_m']:.0f}m<br>
                Food desert score: {row['food_desert_score']}<br>
                Farm type: {row['farm_type']}<br>
            """, max_width=300)
        ).add_to(m)

    m.save('output/urban_ag_map.html')
    print("Map saved to outputs/urban_ag_map.html")