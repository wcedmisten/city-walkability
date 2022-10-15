import json
import requests

MAX_WALK_TIME = 15

starting_lat = 37.53741091416433
starting_lon = -77.41328219109165


def get_amenities(lat, lon):
    payload = {
        "locations":[
            {"lat": lat,"lon": lon}
        ],
        "costing":"pedestrian",
        "denoise":"0.11",
        "generalize":"0",
        "contours":[{"time":MAX_WALK_TIME}],
        "polygons":True
    }


    request = f"http://localhost:8002/isochrone?json={json.dumps(payload)}"
    isochrone = requests.get(request).json()

    geom = json.dumps(isochrone['features'][0]['geometry'])

    query = f"""
    SELECT amenity FROM planet_osm_point
    WHERE ST_Contains(ST_Transform(ST_GeomFromGeoJSON('{geom}'),3857), way) AND amenity IS NOT NULL;
    """

    import psycopg2

    conn = psycopg2.connect(host="localhost", port="15432", dbname="postgres", user="postgres", password="password")
    cur = conn.cursor()

    cur.execute("Select * FROM planet_osm_point LIMIT 0")
    colnames = [desc[0] for desc in cur.description]


    cur.execute(query)
    amenities = list(map(lambda x : x[0], cur.fetchall()))
    
    return amenities


for i in range(20):
    for j in range (20):
        print(get_amenities(starting_lat + .001 * i, starting_lon + .001 * j))
