#!/usr/bin/env python
#
# Creates .kmz map tiles for a Garmin from a larger geo-poisitioned map image. Tested on a 62s
# This crunches and converts an input image (.jpg,.gif,.tiff etc) to match what Garmin devices expect
#
# run 'gentile.py -h' to get the usage.
#
# Connect your GPS via USB and copy the generated kmz files into /Garmin/CustomMap (SD or main mem)
#
# Input image: geo-positioned (lat/long bounding box) in filename. See usage. 
#
# Garmin limitations on .kmz files and images in them:
#  * image must be jpeg, not 'progressive'
#  * only considers the /doc.kml in the .kmz
#  * tiles over 1MP, e.g. > 1024x1024 pixels, 512x2048 pixels do not add increased resolution
#  * each tile jpeg should be less than 3MB.
#  * Max images/tiles per device: typically 100.  500 on some.
#  * smaller image files are rendered faster
#
# requires the following binaries on your system:
#   convert (part of imagemagick)
#   identify (part of imagemagick)
#   zip

import argparse 
import re
import sys
import subprocess
import os
import tempfile
from string import Template


convertProg = 'convert'  # try 'gm convert' for GraphicsMagick equiv
identifyProg = 'identify' # 'gm identify'
zipProg = 'zip'


kmlHeader = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
'''

kmlOverlayTemplate = '''<GroundOverlay>
  <name>$name</name>
  <color>bdffffff</color>
  <drawOrder>$drawingOrder</drawOrder>
  <Icon>
    <href>$tileFileName</href>
    <viewBoundScale>1.0</viewBoundScale>
  </Icon>
  <LatLonBox>
    <north>$north</north>
    <south>$south</south>
    <east>$east</east>
    <west>$west</west>
    <rotation>0.0</rotation>
  </LatLonBox>
</GroundOverlay>
'''

kmlFooter ='''</kml>
'''

def parseArgs():
    '''Returns (args,parser). parser in case you want to dump help'''
    parser = argparse.ArgumentParser(description="Convert a map image to a bunch of map tiles (.kmz files) for your Garmin handheld GPS")

    parser.add_argument('--image', '-i',
                        help='an image file named with its bounding box in decimal degrees. Underscores are required: <map-name>_<North-lat>_<South-lat>_<East-long>_<West-long>.* E.g. Grouse-Mountain_49.336694_49.470628_49.470628_-123.132056_-122.9811.jpg')

    parser.add_argument('--maxTiles', '-t', type=int, default=100,
                        help='Garmin limits the max tiles per model (100 on most, 500 on Montana, Oregon 600 series and GPSMAP 64 series. Tiles of more than 1 megapixel (w*h) add no additional clarity. If you have a large image, it will be reduced in quality until it can be chopped in max-tiles or less 1024x1024 chunks. Defaults to 100.')

    parser.add_argument('--drawingOrder', '-d', type=int, default=51,
                        help='values greater than 50 mean the Garmin device puts this map on top. If you have multiple overlapping maps, set the top one with the highest drawing-order. Defaults to 51.')

    args = parser.parse_args()

    if args.image is None:
        parser.print_help()
        sys.exit(-1)

    return (args,parser)



def getMapAttrsFromArgs(args, parser):
    '''Returns tuple (mapNameStr, northLatFloat, southLatFloat, eastLongFloat, westLongFloat)'''
    m = re.search("([^/_]+)_(-?[0-9]+\.[0-9]+)_(-?[0-9]+\.[0-9]+)_(-?[0-9]+\.[0-9]+)_(-?[0-9]+\.[0-9]+).*", args.image)
    if m is None:
        parser.error(args.image + ' - malformed image file name. Decimal degrees of bounding box required in file name. Use "gentile.py -h" for more details.')
        sys.exit(-1)
    (name,north,south,east,west) = m.groups()
    return (name,float(north),float(south),float(east),float(west))


def getImageWxH(imageFilename):
    '''Returns an int two-tuple (width,height) of the given image file in pixels'''
    whList = subprocess.check_output([identifyProg, '-format', '%w %h', imageFilename]).decode('utf-8').split()
    return (int(whList[0]),int(whList[1]))


def rmrf(startDir):
    '''Danger! equiv of: rm -rf startDir'''
    for (dir,childDirnames,filenames) in os.walk(startDir, topdown=False):
        for f in filenames:
            os.remove(os.path.join(dir,f))
        for d in childDirnames:
            os.rmdir(os.path.join(dir,d))
    os.rmdir(startDir)


def main():
    (args,parser) = parseArgs()
    imageFilename = os.path.abspath(args.image)
    (name,north,south,east,west) = getMapAttrsFromArgs(args,parser)
    (width,height) = getImageWxH(imageFilename)

    # create temp dir and cd there. zip needs working dir so skip working with abs paths
    wdir = tempfile.mkdtemp(prefix='gentile-', dir='.')
    tilesdir = os.path.join(wdir,'tiles')
    os.makedirs(tilesdir)
    os.chdir(wdir)
    tilesdir = 'tiles'

    maxPixels = args.maxTiles * 1024 * 1024
    if (maxPixels < (height * width)):
        newImageFilename = 'tmp1.jpg'
        subprocess.check_output([convertProg, imageFilename, '-resize', '@'+str(maxPixels), newImageFilename])
        imageFilename = newImageFilename

    newImageFilename = 'tmp2.jpg'
    subprocess.check_output([convertProg, imageFilename, '-strip', '-interlace', 'none', newImageFilename ])
    imageFileName = newImageFilename

    # create 1024x1024 tiles from the image in tiledir
    subprocess.check_output([convertProg, '-crop', '1024x1024', imageFilename, '+adjoin', os.path.join(tilesdir, name + '_tile_%03d.jpg')])

    (fullWidth,fullHeight) = getImageWxH(imageFilename)

    template = Template(kmlOverlayTemplate)
    tileNorth = north
    tileWest = west
    tileWidthSum = 0
    dirCount = 0

    # stash each tile in its own kmz file
    for tileFile in sorted(os.listdir('tiles')):
        # right edge or bottom may not be 1024x1024
        (tileWidth,tileHeight) = getImageWxH(os.path.join(tilesdir,tileFile))
        nsDelta = (float(tileHeight)/fullHeight)*(north-south)
        ewDelta = (float(tileWidth)/fullWidth)*((east-west)%360)
        tileWidthSum += tileWidth
        tileEast = tileWest + ewDelta
        tileSouth = tileNorth - nsDelta
        tileName = name + ('_%03d' % dirCount)
        dirCount += 1
        kdir = tileName
        os.makedirs(kdir)
        kmlFile = open(os.path.join(kdir,'doc.kml'), 'w+')
        kmlFile.write(kmlHeader)
        overlay = template.substitute(north=tileNorth, south=tileSouth, east=tileEast, west=tileWest, name=tileFile, drawingOrder=args.drawingOrder, tileFileName=tileFile)
        kmlFile.write(overlay)
        kmlFile.write(kmlFooter)
        kmlFile.close()

        os.rename(os.path.join(tilesdir, tileFile), os.path.join(kdir,tileFile))
        os.chdir(kdir)
        subprocess.check_output([zipProg, '-r', '../' + tileName + '.kmz', '.'])
        os.chdir('..')
        if (tileWidthSum >= fullWidth):
            tileNorth = tileSouth
            tileWest = west
            tileWidthSum = 0
        else:
            tileWest = tileEast

    # move all the kmz files to original working dir and nuke this tmp-dir
    files = os.listdir('.')
    for f in files:
        if f.endswith('.kmz'):
            os.rename(f, '../' + f)
    os.chdir('..')
    rmrf(wdir)


if __name__ == "__main__":
    main()
