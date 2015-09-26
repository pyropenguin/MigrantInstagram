'''
Created on Sep 19, 2015
@license: MIT
The MIT License (MIT)

Copyright (c) 2015 Jonathan Kunze (@pyropenguin)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: pyropenguin
'''
from instagram.client import InstagramAPI
import os
import pickle
import webbrowser
from lxml import etree
from pykml.factory import KML_ElementMaker as KML

def getToken():
   if not os.path.exists('accessToken.txt'):
      print("The first time you run this program, it will need to obtain access to Instagram via")
      print("a token generated from your account. This token will only require basic (read-only)")
      print("access to your account in order to download images. Afterwards, the token will be")
      print("stored in \'accessToken.txt\'. If you ever have problems with this script, delete")
      print("\'accessToken.txt\' and run this script again to regenerate the token.")
       
      client_id = 'd051ace450314ccd8d86fdbff2410a87'
      client_secret = '91c43e9262494f4c82c887a88b21068c'
      redirect_uri = 'http://localhost:8515/oauth_callback'
      scope = ["basic"]
       
      api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
      redirect_uri = api.get_authorize_login_url(scope = scope)
       
      print("Python will now attempt to open the following URL in a web browser:")
      print(redirect_uri)
      print("When it loads, it will go to an invalid URL that looks like")
      print("http://localhost:8515/oauth_callback?code=XXXXXXXXXXXXXXXXXXX")
      print('Copy and paste the code from the address bar (the XXXs in the above example) below.')
      webbrowser.open(redirect_uri)
      
      print("Paste in code in query string after redirect: "),
      code = (str(raw_input().strip()))
      
      access_token = api.exchange_code_for_access_token(code)
      print ("access token: " )
      print (access_token)
      pickle.dump( access_token, open( "accessToken.txt", "wb" ) )


def downloadMedia():
   # Set tag and number of pages to pull
   tag = u'refugeecrisis'
   max_num_pages = 100
   
   # Read Access Token obtained using getToken(), get Instagram API
   access_token_full = pickle.load( open( "accessToken.txt", "rb" ) )
   access_token = access_token_full[0]
   client_secret = "91c43e9262494f4c82c887a88b21068c"
   api = InstagramAPI(access_token=access_token, client_secret=client_secret)
   
   # Retrieve tagged images from Instagram
   print('Grabbing data from Instagram...')
   num_pages = 1
   print(' - Reading page 1/' + str(max_num_pages) + '. 0 images parsed.')
   recent_media, next_ = api.tag_recent_media(33, None, tag)
   if recent_media is None:
      raise NameError('No data retrieved from Instagram!')
   while next_:
      num_pages = num_pages + 1
      print(' - Reading page ' + str(num_pages) +  '/' + str(max_num_pages) + '. ' + 
            str(len(recent_media)) + ' images parsed.')
      max_tag = next_.split('max_tag_id=')[1]
      more_media, next_ = api.tag_recent_media(50, max_tag, tag)
      recent_media.extend(more_media)
      if num_pages >= max_num_pages:
         break

   # Filter out images that do not contain location metadata
   media_filtered = []
   for media in recent_media:
      if media.caption != None:
         try:
            print(str(media.location) + ' ' + 
                  str(media.location.point.latitude) + ' ' +
                  str(media.location.point.longitude)) # If the location isn't set, it will skip to the exception
            media_filtered.append(media)
         except AttributeError:
            pass
         print media.caption.text

   # Save retrieved data in pickle
   pickle.dump( media_filtered, open( "media_filtered.p", "wb" ) )

def buildKML():
   media_filtered = pickle.load( open( "media_filtered.p", "rb" ) )
   
   kml = open('media_KML.kml', "w")
   kmlobj = KML.kml(
       KML.Document(
           KML.Style(
               KML.BalloonStyle(
                   KML.displayMode('default'),
                   KML.text('<b>$[name]</b><br/>$[description]')
               ),
               KML.IconStyle(
                  KML.Icon(
                     KML.href('http://maps.google.com/mapfiles/kml/paddle/red-circle.png'),
                     KML.scale('1.0')
                  ),
                  id='mystyle'
               ),
               id="balloonStyle"
           )
       )
   )

   # add placemarks to the Document element
   for media in media_filtered:
      kmlobj.Document.append(
            KML.Placemark(
               KML.name(media.location.name),
               KML.description("Name: " + media.user.full_name + 
                               "<br>Username: <a href=\"https://instagram.com/" + media.user.username + "/\">" + media.user.username + "</a><br>" +
                               "<img src=" + media.images['standard_resolution'].url + "><br>" +
                               media.caption.text),
               KML.styleUrl('#balloonStyle'),
               KML.TimeStamp(
                  KML.when(media.created_time.isoformat() + 'Z')
               ),
               KML.Point(
                  KML.extrude(1),
                  KML.altitudeMode('relativeToGround'),
                  KML.coordinates('{lon},{lat},{alt}'.format(
                      lon=media.location.point.longitude,
                      lat=media.location.point.latitude,
                      alt=0,
               ),
            ),
         ),
      )
   )
   kml.write(etree.tostring(etree.ElementTree(kmlobj),pretty_print=True))
   kml.close()
   
   os.system('open /Applications/\"Google Earth Pro.app\" media_KML.kml')


if __name__ == '__main__':
   getToken()
   downloadMedia()
   buildKML()
