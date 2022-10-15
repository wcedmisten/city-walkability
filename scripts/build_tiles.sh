#!/bin/bash

mkdir /data/valhalla_tiles
valhalla_build_config --mjolnir-tile-dir /data/valhalla_tiles --mjolnir-tile-extract /data/valhalla_tiles.tar --mjolnir-timezone /data/valhalla_tiles/timezones.sqlite --mjolnir-admin /data/valhalla_tiles/admins.sqlite > /data/valhalla.json

valhalla_build_timezones > /data/valhalla_tiles/timezones.sqlite

valhalla_build_tiles -c /data/valhalla.json /data/data.osm.pbf

valhalla_build_extract -c /data/valhalla.json -v
