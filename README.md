Quickstart
==========

*gentile.py* is a quick hack that will convert a jpeg of a map into
tiles that Garmin GPS units can display instead of the regular
basemap.  

run it like this:

    gentile.py -t 30 -i North-Shore_49.470808_49.336874_-122.980824_-123.131780.jpg   

and it will split it into 1024x1024 pixel geo-anchored jpegs, all wrapped in one kmz file:

    North-Shore.kmz

Plug in your GPS via USB and copy the kmz files to its /Garmin/CustomMaps/ directory.  These map tiles should now be 
displayed on your GPS when you look at that area.

System Requirements
===================

* python 2.7
* imagemagick convert & identify programs (or graphicsmagick variants)
* zip

Tested on OS X 10.10 using brew to install imagemagick.  

Map File Names
==============

Maps can be jpeg, tiff or other formats supported by ImageMagick. The
file name of your map must include its bounding box (lat/long) in
decimal degrees. The syntax is:
  
    North-Shore_49.470808_49.336874_-122.980824_-123.131780.jpg   

    <name>_<north-lattitude>_<south_lattitude>_<east-longitude>_<west_longitude>[.type]

Don't use underscore anywhere in the name except as one of the four separators above. 


Figuring Out The Bounding Box
=============================

Try using GoogleEarth to load an image (Add->Image Overlay) and
fiddling with the coordinates in the Location tab to postion the map.
Then try those coordinates with gentile.py.  Tune it by using the GPS
with the kmz files and observe if it is offset N-S and/or E-W.
Regenerate the tiles with adjusted coordinates.

How Many Tiles
==============

The '-t' parameter suggests the maximum number of tiles to
generate. Setting it too low may make for grainy tile images because
gentile.py will reduce the resolution of (a copy of) the image until it
can be cut it into ~maxtiles 1024x1024 pieces.

Setting maxtiles too high may exceed the capacity of your GPS device.  A
Garmin 62s can hold a maxiumum of 100 tiles while some other models support 500.

Run the following for other options:
  
   gentile.py -h
