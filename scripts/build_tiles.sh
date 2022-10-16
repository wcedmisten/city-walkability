#!/bin/bash

mkdir /data/valhalla_tiles

if ! test -f "/data/valhalla.json"; then
    echo "Valhalla JSON not found. Creating config." 
    valhalla_build_config --mjolnir-tile-dir /data/valhalla_tiles --mjolnir-tile-extract /data/valhalla_tiles.tar --mjolnir-timezone /data/valhalla_tiles/timezones.sqlite --mjolnir-admin /data/valhalla_tiles/admins.sqlite > /data/valhalla.json
fi

if ! test -f "/data/valhalla_tiles/timezones.sqlite"; then
    echo "Valhalla tiles not found. Building now."
    valhalla_build_timezones > /data/valhalla_tiles/timezones.sqlite
    valhalla_build_tiles -c /data/valhalla.json /data/data.osm.pbf
fi

if ! test -f "/data/valhalla_tiles.tar"; then
    echo "Tile extract not found. Extracting now."
    valhalla_build_extract -c /data/valhalla.json -v
fi

echo "Starting valhalla server."
valhalla_service /data/valhalla.json 1
