var fs = require('fs');
var csv = require('csv');

var parser = csv.parse({delimiter: '\t',columns: ['country_code', 'postal_code', 'place_name', 'admin_name_1', 'admin_code_1', 'admin_name_2', 'admin_code_2', 'admin_name_3', 'admin_code_3','latitude', 'longitude', 'accuracy']}, function(err, data){
    var geojson = {
        "type": "FeatureCollection",
        "features": []
    };

    for( var i = 0; i < data.length; i++ ){
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [parseFloat(data[i]['longitude']), parseFloat(data[i]['latitude'])]
            },
            "properties": {
                "country_code": data[i]['country_code'],
                "postal_code": data[i]['postal_code'],
                "place_name": data[i]['place_name'],
                "admin_name_1": data[i]['admin_name_1'],
                "admin_code_1": data[i]['admin_code_1'],
                "admin_name_2": data[i]['admin_name_2'],
                "admin_code_2": data[i]['admin_code_2'],
                "admin_name_3": data[i]['admin_name_3'],
                "admin_code_3": data[i]['admin_code_3']
            }
        };
        geojson['features'].push(feature);
    }

    console.log(JSON.stringify(geojson));
});

fs.createReadStream(__dirname+'/tmp/PK.txt').pipe(parser);
