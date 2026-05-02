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
                Land Use: {row['land_use']}<br>
                Score: {row['score']}<br>
                Transit Distance: {row['transit_distance_m']:.0f}m<br>
                Sun Hours: {row['sun_hours']:.0f} kWh<br>
                Food Desert Score: {row['food_desert_score']}
            """, max_width=250)
        ).add_to(m)

    m.save('output/urban_ag_map.html')
    print("Map saved to outputs/urban_ag_map.html")