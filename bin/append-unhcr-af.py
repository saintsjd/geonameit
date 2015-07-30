# -*- coding: utf-8 -*-
import json
import psycopg2

DSN = "dbname=jonsaints"

unhcr = {}

with psycopg2.connect(DSN) as conn:
    with conn.cursor() as curs:
        SQL = '''
            select
            distinct on (g.village_na)
            g.village_na,
            p.uuid, st_area(p.geom) as area,
            g.population
            from polygons p
            inner join afg_ppl g on ST_Intersects(g.buffered,p.geom)
            order by g.village_na, area desc, p.uuid ;
        '''
        curs.execute(SQL)

        for row in curs:
            uuid = row[1]
            name = row[0]
            population = row[3]
            if uuid not in unhcr:
                unhcr[uuid] = []
            unhcr[uuid].append(name)

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
        print feature['properties']['UUID'], unhcr[feature['properties']['UUID']]
        #feature['properties']['unhcr'] = sorted(unhcr[feature['properties']['UUID']], key=lambda tup: tup[1])
        feature['properties']['unhcr'] = unhcr[feature['properties']['UUID']]
    else:
        feature['properties']['unhcr'] = []
    export['features'].append(feature)
    if i % 1000 == 0:
        print i

with open('output/village_final_geonames_unhcr.json','wb') as f:
    f.write(json.dumps(export))
