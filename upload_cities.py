import glob
import psycopg2

conn = psycopg2.connect(host="localhost", port="15432", dbname="postgres", user="postgres", password="password")
cur = conn.cursor()

create_city_table = """CREATE TABLE IF NOT EXISTS city (
    name text PRIMARY KEY,
	geom geometry
);
"""

cur.execute(create_city_table)
conn.commit()

import json

state = "va"


def create_va_city(city):
    with open(f"geojson-us-city-boundaries/cities/{state}/{city}.json") as f:
        data = json.load(f)

    geom = data['features'][0]['geometry']

    cur.execute("INSERT INTO city (name, geom) VALUES (%s, %s)", (city, json.dumps(geom)))
    conn.commit()

for city_file in glob.glob(f'geojson-us-city-boundaries/cities/{state}/*'):
    city = city_file.split("/")[-1].split(".json")[0]
    create_va_city(city)
