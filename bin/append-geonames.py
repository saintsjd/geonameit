import json
import psycopg2

DSN = "dbname=jonsaints"

geonames = {}

with psycopg2.connect(DSN) as conn:
    with conn.cursor() as curs:
        SQL = '''
            select
            distinct on (g.name)
            g.name,
            g.population,
            p.uuid, st_area(p.geom) as area
            from polygons p
            inner join geonames g on ST_Intersects(g.buffered,p.geom)
            order by g.name, p.area desc, p.uuid;
        '''
        curs.execute(SQL)

        for row in curs:
            uuid = row[2]
            name = row[0]
            # NOTE popluation is not used for ranking geonames because most of this dataset have zero for popluation values
            population = row[1]
            if uuid not in geonames:
                geonames[uuid] = []
            geonames[uuid].append(unicode(name,'utf-8'))

geojson = []
with open('input/village_with_pop_dates.json') as f:
    geojson = json.loads(f.read())

export = {
    "type": "FeatureCollection",
    "features": []
    }

i = 0
for feature in geojson['features']:
    i += 1
    if feature['properties']['UUID'] in geonames:
        #print feature['properties']['UUID'], geonames[feature['properties']['UUID']]
        #feature['properties']['geonames'] = sorted(geonames[feature['properties']['UUID']], key=lambda tup: tup[1])
        feature['properties']['geonames'] = geonames[feature['properties']['UUID']]
    else:
        feature['properties']['geonames'] = []
    export['features'].append(feature)
    if i % 1000 == 0:
        print i

with open('output/village_final_popcounts_geonames.json','wb') as f:
    f.write(json.dumps(export))
