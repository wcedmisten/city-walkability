import json
import glob
import requests
import psycopg2
from collections import defaultdict
import poisson_disc
import shapely.wkt
import numpy as np
import folium
from util import get_cities


MAX_WALK_TIME = 15

conn = psycopg2.connect(host="localhost", port="15432", dbname="postgres", user="postgres", password="password")
cur = conn.cursor()

seen_amenities = defaultdict(lambda: 0)

def to_dict(colnames, rows):
    res = []

    for row in rows:
        row_dict = {}
        for colname, x in zip(colnames, row):
            if x:
                if colname == "amenity" or colname == "shop" or colname == "leisure":
                    seen_amenities[f"{colname}:{x}"] += 1
                row_dict[colname] = x
        
        res.append(row_dict)

    return res

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
    SELECT * FROM planet_osm_point
    WHERE ST_Contains(ST_Transform(ST_GeomFromGeoJSON('{geom}'),3857), way) AND (amenity IS NOT NULL OR shop IS NOT NULL OR leisure IS NOT NULL);
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.execute("SELECT * FROM planet_osm_point LIMIT 0")
    colnames = [desc[0] for desc in cur.description]
    
    return to_dict(colnames, rows)


amenities_list = set([
    "amenity:cafe",
    "amenity:bar",
    "amenity:pub",
    "amenity:restaurant",
    "shop:bakery",
    "shop:convenience",
    "shop:supermarket",
    "shop:department_store",
    "shop:clothes",
    "shop:shoes",
    "shop:books",
    "shop:hairdresser",
    "leisure:fitness_center",
    "leisure:park"
])

def num_unique_amenities(rows):
    """Returns the number of unique amenities, not double-counting amenities of the same type"""
    unique_amenities = set()

    for row in rows:
        if "amenity" in row and f"amenity:{row['amenity']}" in amenities_list:
            unique_amenities.add(f"amenity:{row['amenity']}")
            continue
        if "shop" in row and f"shop:{row['shop']}" in amenities_list:
            unique_amenities.add(f"shop:{row['shop']}")
            continue
        if "leisure" in row and f"leisure:{row['leisure']}" in amenities_list:
            unique_amenities.add(f"leisure:{row['leisure']}")
            continue

    return len(unique_amenities)

state = "va"

def get_avg_unique_amenities(city, state):
    # generate points inside a city bbox

    # get bbox for city
    get_bbox_query = """SELECT ST_AsText(ST_Envelope( geom ))
    FROM ( SELECT geom FROM city WHERE name=%s AND state=%s ) as geom
    """
    cur.execute(get_bbox_query, [city, state])
    bbox = cur.fetchone()

    # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = shapely.wkt.loads(bbox[0]).bounds

    height = (maxy - miny)
    width = (maxx - minx)

    points = poisson_disc.Bridson_sampling(dims=np.array([width,height]), radius=.005)


    is_in_query = """
    SELECT ST_Contains(geom, ST_GeomFromText('POINT(%s %s)'))
    FROM ( SELECT geom FROM city WHERE name=%s AND state=%s ) as geom
    """

    scaled = list(map(lambda p: [p[0] + minx, p[1] + miny], points))

    def point_in_city(point):
        is_in_city = cur.execute(is_in_query, [point[0], point[1], city, state])
        return cur.fetchone()[0]

    in_city = list(filter(point_in_city, scaled))

    total_unique_amenities = 0

    for lon, lat in in_city:
        amenities = get_amenities(lat, lon)

        num_unique = num_unique_amenities(amenities)
        total_unique_amenities += num_unique

    if len(in_city) == 0:
        return 0

    return total_unique_amenities / len(in_city)


res = {}

with open("results.json") as f:
    results = json.load(f)

for city, state in get_cities():
    # score = get_avg_unique_amenities(city, state)
    
    print(city, state, results[city])

    res[city + " " + state] = results[city]

print(res)