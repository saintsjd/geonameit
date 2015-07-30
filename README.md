# geonameit
Append geonames to a geojson file

This project uses `make`. For more information about why make is a good way to organize small data science projects see http://bost.ocks.org/mike/make/

## Usage:

You need to have a postgis server for this to work. Right now it only runs on a local postgres install. We could easily change it to connect to an external postgres database.

Then, put the file you want to append with geonames and unhcr names in the input folder. Right now it must be input/village_final.json or you can edit the make file to access a different file.

Then open the command line and change directory into this folder. Then run `make`

The make file will append the names and create output in the `output` folder. Geojson and shapefiles appended with the names.

To run again just

~~~
make clean
make
~~~
