.PHONY: clean

all: output/final-32642.shp output/final-32642.json

clean:
	rm -rf ./output
	rm -rf ./tmp

tmp/init:
	mkdir -p ./output
	mkdir -p ./tmp
	touch tmp/init

tmp/PK.zip: tmp/init
	wget -N http://download.geonames.org/export/dump/PK.zip
	mv PK.zip tmp/
	touch tmp/PK.zip

tmp/AF.zip: tmp/init
	wget -N http://download.geonames.org/export/dump/AF.zip
	mv AF.zip tmp/
	touch tmp/AF.zip

tmp/PK.txt: tmp/PK.zip
	unzip -o -d ./tmp tmp/PK.zip
	touch tmp/PK.txt

tmp/AF.txt: tmp/AF.zip
	unzip -o -d ./tmp tmp/AF.zip
	touch tmp/AF.txt

tmp/postgres_create_geonames_table: tmp/init
	psql -c 'drop table if exists import_geonames;'
	psql -c 'create table import_geonames (geonameid integer, name varchar, asciiname varchar, alternatenames varchar, latitude numeric, longitude numeric, feature_class varchar, feature_code varchar, country_code varchar, cc2 varchar, admin1_code varchar, admin2_code varchar, admin3_code varchar, admin4_code varchar, population integer, elevation integer, dem varchar, timezone varchar, modification_date varchar);'
	touch tmp/postgres_create_geonames_table

tmp/import_geonames: tmp/postgres_create_geonames_table tmp/AF.txt tmp/PK.txt
	cat tmp/PK.txt | psql -c "copy import_geonames from STDIN NULL '';"
	cat tmp/AF.txt | psql -c "copy import_geonames from STDIN NULL '';"
	touch tmp/import_geonames

tmp/index_geonames: tmp/import_geonames
	psql -c 'drop table if exists geonames;'
	psql -c 'create table geonames as select *, st_point(longitude,latitude) as geom, st_setsrid(st_envelope(st_buffer(st_point(longitude,latitude)::geography,200)::geometry),4326) as buffered from import_geonames'
	psql -c "SELECT UpdateGeometrySRID('geonames','geom',4326);"
	psql -c "SELECT UpdateGeometrySRID('geonames','buffered',4326);"
	psql -c 'create index index_geonames_geom on geonames using GIST (geom);'
	psql -c 'create index index_geonames_buffered on geonames using GIST (buffered);'
	touch tmp/index_geonames

tmp/import-polygons: tmp/init input/village_with_pop_dates.json bin/import-polygons.py
	psql -c 'drop table if exists polygons;'
	psql -c 'create table polygons (geom geometry, uuid varchar, buffered geometry, area numeric );'
	python bin/import-polygons.py
	psql -c "SELECT UpdateGeometrySRID('polygons','geom',4326);"
	psql -c 'drop index if exists index_polygons_geom'
	psql -c 'create index index_polygons_geom on polygons using GIST (geom);'
	touch tmp/import-polygons

output/village_with_pop_dates_geonames.json: input/village_with_pop_dates.json tmp/import-polygons tmp/index_geonames bin/append-geonames.py
	python bin/append-geonames.py

tmp/afg_ppl_settlement_pnt_shp.zip: tmp/init
	wget -O tmp/afg_ppl_settlement_pnt_shp.zip -N http://www.humanitarianresponse.info/sites/www.humanitarianresponse.info/files/afg_ppl_settlement_pnt_shp.zip
	touch tmp/afg_ppl_settlement_pnt_shp.zip

tmp/afg_ppl_settlement_pnt.shp: tmp/afg_ppl_settlement_pnt_shp.zip
	unzip -o -d ./tmp tmp/afg_ppl_settlement_pnt_shp.zip
	touch tmp/afg_ppl_settlement_pnt.shp

tmp/import-afg-ppl: tmp/afg_ppl_settlement_pnt.shp
	psql -c 'drop table if exists import_afg_ppl;'
	shp2pgsql -s 4326 ./tmp/afg_ppl_settlement_pnt import_afg_ppl | psql
	psql -c 'drop table if exists afg_ppl;'
	psql -c 'create table afg_ppl as select *, st_setsrid(st_envelope(st_buffer(geom::geography,200)::geometry),4326) as buffered from import_afg_ppl'
	touch tmp/import-afg-ppl

tmp/import-unhcr: input/unhcr-utf.csv tmp/init
	psql -c 'drop table if exists import_unhcr;'
	psql -c 'create table import_unhcr (num varchar, name varchar, census_1981 varchar,	census_1998 varchar, estimate_2000 varchar,	calculation_2010 varchar, annual_growth varchar, latitude numeric,longitude numeric, parent_division varchar, name_variants varchar );'
	cat input/unhcr-utf.csv | psql -c "copy import_unhcr from STDIN DELIMITER ',' CSV;"
	psql -c 'drop table if exists unhcr;'
	psql -c 'create table unhcr as select *, st_point(longitude,latitude) as geom, st_setsrid(st_envelope(st_buffer(st_point(longitude,latitude)::geography,200)::geometry),4326) as buffered from import_unhcr'
	psql -c "SELECT UpdateGeometrySRID('unhcr','geom',4326);"
	psql -c "SELECT UpdateGeometrySRID('unhcr','buffered',4326);"
	psql -c 'create index index_unhcr_geom on unhcr using GIST (geom);'
	psql -c 'create index index_unhcr_buffered on unhcr using GIST (buffered);'
	touch tmp/import-unhcr

# SINDH
output/village_with_pop_dates_geonames_unhcr.json: output/village_with_pop_dates_geonames.json tmp/import-unhcr bin/append-unhcr.py
	python bin/append-unhcr.py

# FARAH
# output/village_with_pop_dates_geonames_unhcr.json: output/village_with_pop_dates_geonames.json tmp/import-afg-ppl bin/append-unhcr-af.py
# 	python bin/append-unhcr-af.py

output/village_with_pop_dates_geonames_unhcr_primary_names.json: output/village_with_pop_dates_geonames_unhcr.json bin/append-primary-name.py
	python bin/append-primary-name.py

output/final.json: output/village_with_pop_dates_geonames_unhcr_primary_names.json bin/final.py
	python bin/final.py

output/final-32642.shp: output/final.json
	rm -f ./output/final-32642.shp
	ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 ./output/final-32642.shp -t_srs "EPSG:32642" output/final.json

output/final-32642.json: output/final.json
	rm -f ./output/final-32642.json
	ogr2ogr -f "GeoJSON" ./output/final-32642.json -t_srs "EPSG:32642" output/final.json



# tmp/import-unhcr: input/unhcr-utf.csv tmp/import-afg-ppl tmp/init
# 	psql -c 'drop table if exists import_unhcr;'
# 	psql -c 'create table import_unhcr (num varchar, name varchar, census_1981 varchar,	census_1998 varchar, estimate_2000 varchar,	calculation_2010 varchar, annual_growth varchar, latitude numeric,longitude numeric, parent_division varchar, name_variants varchar );'
# 	cat input/unhcr-utf.csv | psql -c "copy import_unhcr from STDIN DELIMITER ',' CSV;"
# 	psql -c 'drop table if exists unhcr;'
# 	psql -c 'create table unhcr as select *, st_point(longitude,latitude) as geom, st_setsrid(st_envelope(st_buffer(st_point(longitude,latitude)::geography,200)::geometry),4326) as buffered from import_unhcr'
# 	psql -c "SELECT UpdateGeometrySRID('unhcr','geom',4326);"
# 	psql -c "SELECT UpdateGeometrySRID('unhcr','buffered',4326);"
# 	psql -c 'create index index_unhcr_geom on unhcr using GIST (geom);'
# 	psql -c 'create index index_unhcr_buffered on unhcr using GIST (buffered);'
# 	touch tmp/import-unhcr
#
# output/village_with_pop_dates_unhcr.json: output/village_with_pop_dates_geonames.json tmp/import-unhcr bin/append-unhcr.py tmp/import-afg-ppl
# 	python bin/append-unhcr.py
# tmp/PK.geojson: tmp/PK.txt tsv2geojson.js
# 	node tsv2geojson.js > tmp/PK.geojson
