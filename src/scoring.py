

#creating a scoring function to assess viabilities of different areas.

def score_parcel(sun_hours, food_desert_score,transit_distance, lot_size):
    score = 0

    score += min(sun_hours/2000,1) * 30   ## capping sun hours here to convert to a 0-1 scale. 
    score += food_desert_score * 25
    score += max(0, 1 - transit_distance/1000) * 20
    score += min(lot_size/10000, 1) * 25  ## capping lot size area to 10000, can alter

    return round(score, 2)



print(score_parcel(1800, 0.8, 300, 8000))