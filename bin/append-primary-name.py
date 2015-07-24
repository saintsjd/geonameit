# -*- coding: utf-8 -*-
import json

geojson = []
with open('output/AF_village_final_popcounts_geonames_unhcr.json') as f:
    geojson = json.loads(f.read())

export = {
    "type": "FeatureCollection",
    "features": []
    }

i = 0
for feature in geojson['features']:
    i += 1

    feature['properties']['primary_name'] = ""

    if ('geonames' in feature['properties'] and feature['properties']['geonames']):
        feature['properties']['primary_name'] = feature['properties']['geonames'][0]

    if ( 'unhcr' in feature['properties'] and feature['properties']['unhcr']):
        feature['properties']['primary_name'] = feature['properties']['unhcr'][0]

    export['features'].append(feature)
    if i % 1000 == 0:
        print i

with open('output/AF_village_final_popcounts_geonames_unhcr_primary_names.json','wb') as f:
    f.write(json.dumps(export))
