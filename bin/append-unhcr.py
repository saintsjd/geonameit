# -*- coding: utf-8 -*-
import json
import psycopg2

DSN = "dbname=jonsaints"

unhcr = {}

with psycopg2.connect(DSN) as conn:
    with conn.cursor() as curs:
        SQL = '''
            select
            distinct on (g.name)
            g.name,
            p.uuid, st_area(p.geom) as area
            from polygons p
            inner join unhcr g on st_overlaps(g.buffered,p.geom)
            order by g.name, p.uuid, area desc;
        '''
        curs.execute(SQL)

        for row in curs:
            uuid = row[1]
            name = row[0]
            if uuid not in unhcr:
                unhcr[uuid] = []
            unhcr[uuid].append(unicode(name,'utf-8'))

geojson = []
with open('output/village_final_geonames.json') as f:
    geojson = json.loads(f.read())

export = {
    "type": "FeatureCollection",
    "features": []
    }

i = 0
for feature in geojson['features']:
    i += 1
    if feature['properties']['UUID'] in unhcr:
        # print feature['properties']['UUID'], unhcr[feature['properties']['UUID']]
        feature['properties']['unhcr'] = unhcr[feature['properties']['UUID']]
    else:
        feature['properties']['unhcr'] = []
    export['features'].append(feature)

with open('output/village_final_geonames_unhcr.json','wb') as f:
    f.write(json.dumps(export))
