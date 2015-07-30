import json
import psycopg2

DSN = "dbname=jonsaints"

with open('input/village_final.json') as f:
    geojson = json.loads(f.read())

    SQL = ""
    if 'features' in geojson and len(geojson['features']) > 0:
        i = 0
        for feature in geojson['features']:
            SQL += """
                insert into polygons
                (geom, uuid, area)
                values
                (st_geomfromgeojson('{}'),'{}', st_area(st_geomfromgeojson('{}')::geography));
            """.format( json.dumps(feature['geometry']), feature['properties']['UUID'], json.dumps(feature['geometry']) )
            i += 1

            if i % 1000 == 0:
                print i

        print "writing {}".format(i)
        with psycopg2.connect(DSN) as conn:
            with conn.cursor() as curs:
                curs.execute(SQL)
    else:
        print "no features {}".format(fname)
