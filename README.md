# MigrantInstagram
A KML visualization of geotagged Instagram media related to the movement of Syrian migrant crisis.
Data obtained from Instagram hashtag refugeecrisis

## Requirements
- Python 2.x: https://www.python.org
- python-instagram (Official Instagram API for Python): https://github.com/Instagram/python-instagram
- lxml: http://lxml.de
- pyKML: https://pythonhosted.org/pykml/

## Usage
1. Install the above software packages
2. Run GetTaggedImages.py
3. GetTaggedImages.py will get a user token from your Instagram account. You will need to sign into your Instagram, then copy/paste the code you get after sign-in into the Python terminal.
4. GetTaggedImages.py will pull the Instagram results, filter out those that don't have geotags, and save them as a pickled file called "media_filtered.p". You can use this file for further analysis if you'd like.
5. GetTaggedImages.py will build "media_KML.kml", which you can open with Google Earth.
6. When you load "media_KML.kml" in Google Earth, you can visually explore the images plotted across the globe.

