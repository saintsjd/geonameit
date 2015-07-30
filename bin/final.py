# -*- coding: utf-8 -*-
import json
import psycopg2
import math

DSN = "dbname=jonsaints"

areas = {}

with psycopg2.connect(DSN) as conn:
    with conn.cursor() as curs:
        SQL = '''
            select
            uuid,
            st_area(geom::geography) as area
            from polygons p
        '''
        curs.execute(SQL)

        for row in curs:
            uuid = row[0]
            area = row[1]
            areas[uuid] = area


geojson = []
with open('output/village_final_geonames_unhcr_primary_names.json') as f:
    geojson = json.loads(f.read())

export = {
    "type": "FeatureCollection",
    "features": []
    }

i = 0
for feature in geojson['features']:
    i += 1
    f = {}
    f['geometry'] = feature['geometry']
    f['properties'] = {}
    if feature['properties']['UUID'] in areas:
        f['properties']['areasqutm'] = int(math.ceil(areas[ feature['properties']['UUID'] ]))
    else:
        print "no area", feature['properties']['UUID']
        f['properties']['areasqutm'] = None
    f['properties']['uuid'] = feature['properties']['UUID']
    f['properties']['mindate'] = feature['properties']['mindate']
    f['properties']['maxdate'] = feature['properties']['maxdate']
    f['properties']['pr_name'] = feature['properties']['primary_name']
    #f['properties']['dgpc_ls'] = int(math.ceil( float(feature['properties']['PopCount']) ))
    f['properties']['dgpc_ls'] = feature['properties']['PopCount']

    f['properties']['unhrname'] = ""
    if len(feature['properties']['unhcr']) > 1 :
        f['properties']['unhrname'] = "AGG[{}]".format( ",".join(feature['properties']['unhcr']) )
    elif len(feature['properties']['unhcr']) == 1:
        f['properties']['unhrname'] = feature['properties']['unhcr'][0]

    f['properties']['geoname'] = ""
    if len(feature['properties']['geonames']) > 1 :
        f['properties']['geoname'] = "AGG[{}]".format( u','.join(feature['properties']['geonames']).encode('utf-8').strip() )
    elif len(feature['properties']['geonames']) == 1:
        f['properties']['geoname'] = feature['properties']['geonames'][0]

    export['features'].append(f)

with open('output/final.json','wb') as f:
    f.write(json.dumps(export))
