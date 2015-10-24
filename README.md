Quickstart
==========

*gentile.py* is a quick hack that will convert a jpeg of a map into
tiles that Garmin GPS units can display instead of the regular
basemap.  

run it like this:

    gentile.py -t 30 -i North-Shore_49.470808_49.336874_-122.980824_-123.131780.jpg   

and it will split it into 1024x1024 pixel tile jpegs, each wrapped in a kmz file:

    North-Shore_000.kmz	North-Shore_007.kmz	North-Shore_014.kmz	North-Shore_021.kmz	North-Shore_028.kmz
    North-Shore_001.kmz	North-Shore_008.kmz	North-Shore_015.kmz	North-Shore_022.kmz	North-Shore_029.kmz
    North-Shore_002.kmz	North-Shore_009.kmz	North-Shore_016.kmz	North-Shore_023.kmz	North-Shore_030.kmz
    North-Shore_003.kmz	North-Shore_010.kmz	North-Shore_017.kmz	North-Shore_024.kmz	North-Shore_031.kmz
    North-Shore_004.kmz	North-Shore_011.kmz	North-Shore_018.kmz	North-Shore_025.kmz	North-Shore_032.kmz
    North-Shore_005.kmz	North-Shore_012.kmz	North-Shore_019.kmz	North-Shore_026.kmz	North-Shore_033.kmz
    North-Shore_006.kmz	North-Shore_013.kmz	North-Shore_020.kmz	North-Shore_027.kmz	North-Shore_034.kmz

Plug in your GPS via USB and copy the kmz files to its /Garmin/CustomMaps/ directory.  These map tiles should now be 
displayed on your GPS when you look at that area.

System Requirements
===================

* python 2.7
* imagemagick
* zip

Tested on OS X 10.10 using brew to install imagemagick.  

Map File Names
==============

Maps can be jpeg, tiff or other formats supported by ImageMagick. The
file name of your map must include its bounding box (lat/long) in
decimal degrees. The syntax is:
  
    North-Shore_49.470808_49.336874_-122.980824_-123.131780.jpg   

    <name>_<north-lattitude>_<south_lattitude>_<east-longitude>_<west_longitude>

Don't use underscore anywhere in the name except as one of the four separators above. 


Figuring Out The Bounding Box
=============================

Try using GoogleEarth (Add->Image Overlay) and fiddling with the
coordinates in the Location tab to postion the map.  Then try those
coordinates with gentile.py.  Tune it by using the GPS with the kmz
files and observe if it's offset N-S and/or E-W.  Regenerate the tiles
with adjusted coordinates.

How Many Tiles
==============

The '-t' parameter suggests the maximum number of tiles to
generate. Setting too low may make for grainy tile images because
gentile.py will reduce the resolution of the image until it can be cut
it into ~maxtiles 1024x1024 pieces.

Setting maxtiles too high may exceed the capacity of your GPS device.  A
Garmin 62s can hold a maxiumum of 100 tiles while some other models support 500

Run the following for other options:
  
   gentile.py -h
