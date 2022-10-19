import glob
import psycopg2
import json

from util import get_cities

conn = psycopg2.connect(host="localhost", port="15432", dbname="postgres", user="postgres", password="password")
cur = conn.cursor()

create_city_table = """CREATE TABLE IF NOT EXISTS city (
    name text,
    state text,
	geom geometry,
    PRIMARY KEY (name, state)
);
"""

cur.execute(create_city_table)
conn.commit()


def import_city(city, state):
    with open(f"geojson-us-city-boundaries/cities/{state}/{city}.json") as f:
        data = json.load(f)

    geom = data['features'][0]['geometry']

    cur.execute("INSERT INTO city (name, state, geom) VALUES (%s, %s, %s)", (city, state, json.dumps(geom)))
    conn.commit()



for city, state in get_cities():
    # print(city,state)
    import_city(city, state)
