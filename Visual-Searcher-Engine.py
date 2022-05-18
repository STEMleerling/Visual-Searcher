# Created by Maarten De Nocker on 14/11/2021
# Tool to get data from Flickr API

import urllib.parse
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime, timedelta

# global variables-----------------------------------------------------------------------------------------------------
date_format = "%Y-%m-%d"
id = []
owner = []
secret = []
title = []
date_taken = []
views = []
tags = []
machine_tags = []
lat = []
long = []
accuracy = []
context = []

# ask for api key + criteria-------------------------------------------------------------------------------------------

# getting data---------------------------------------------------------------------------------------------------------

 # url for testing-----------------------------------------------------------------------------------------------------
page = '1'
min_taken_date = '2018-01-01'
max_taken_date = '2018-03-31'
min_taken_date_input = min_taken_date
max_taken_date_input = max_taken_date
en = '&'
mid_url = 'safe_search=&woe_id=&media=&has_geo=1&geo_context=&lat=&lon=&radius=&radius_units=km&per_page=250'
end_url = '&sort=date-taken-asc&extras=geo,date_taken,tags,machine_tags,description,views&format=rest'
url = 'https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=f738988d1955a1c8f1e7fcfb981af6b4&tags=wolf&text=wolf&min_upload_date=&max_upload_date='\
      + en + urllib.parse.urlencode({'min_taken_date': min_taken_date})\
      + en + urllib.parse.urlencode({'max_taken_date': max_taken_date})\
      + en + mid_url\
      + en + urllib.parse.urlencode({'page': page})\
      + end_url
print("url from where data wil be fetched: "+ url + "\n")

 # fetching data-------------------------------------------------------------------------------------------------------
print("debug messages:")
fully_scanned = 0
while fully_scanned == 0:
      # split data into different packages to stay under 250 (split phase)---------------------------------------------
      xml_data = requests.get(url)
      parser = ET.XMLParser(encoding="utf-8")
      root = ET.fromstringlist(xml_data, parser=parser)
      total = int(root[0].attrib['total'])
      while total >= 250:
            if min_taken_date == max_taken_date:
                  print("error: request is to large, add more parameters\n"
                        "(one day in your timeframe has to many items(>250))")
            print("data not under 250 items per packages\n"
                  "splitting data")
            # calculate delta between the 2 dates
            min_taken_date_not_string = datetime.strptime(min_taken_date, date_format)
            max_taken_date_not_string = datetime.strptime(max_taken_date, date_format)
            delta = max_taken_date_not_string - min_taken_date_not_string
            print("delta between the two given dates: " + str(delta.days))
            end_date = min_taken_date_not_string + timedelta(days=int(delta.days/2))
            print("delta divided by 2: " + str(delta.days/2))
            print("new end date for url: " + str(end_date))
            max_taken_date = end_date.strftime(date_format)
            url = 'https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=f738988d1955a1c8f1e7fcfb981af6b4&tags=wolf&text=wolf&min_upload_date=&max_upload_date=' \
                  + en + urllib.parse.urlencode({'min_taken_date': min_taken_date}) \
                  + en + urllib.parse.urlencode({'max_taken_date': max_taken_date}) \
                  + en + mid_url \
                  + en + urllib.parse.urlencode({'page': page}) \
                  + end_url
            print("new url: " + url)
            xml_data = requests.get(url)
            parser = ET.XMLParser(encoding="utf-8")
            root = ET.fromstringlist(xml_data, parser=parser)
            total = int(root[0].attrib['total'])
            print()
      # get data from this packages into lists-------------------------------------------------------------------------
      print("place data into lists")
      '''xml_data = requests.get(url)
      parser = ET.XMLParser(encoding="utf-8")
      root = ET.fromstringlist(xml_data, parser=parser)
      total = int(root[0].attrib['total'])
      '''
      print("total items in package: " + str(total))
      for i in range(total):
            print("step " + str(i))
            photo_id = root[0][i].attrib['id']
            id.append(photo_id)
            photo_owner = root[0][i].attrib['owner']
            owner.append(photo_owner)
            photo_secret = root[0][i].attrib['secret']
            secret.append(photo_secret)
            photo_title = root[0][i].attrib['title']
            title.append(photo_title)
            photo_datetaken = root[0][i].attrib['datetaken']
            date_taken.append(photo_datetaken)
            photo_views = root[0][i].attrib['views']
            views.append(photo_views)
            photo_tags = root[0][i].attrib['tags']
            tags.append(photo_tags)
            photo_machine_tags = root[0][i].attrib['machine_tags']
            machine_tags.append(photo_machine_tags)
            photo_lat = root[0][i].attrib['latitude']
            lat.append(photo_lat)
            photo_long = root[0][i].attrib['longitude']
            long.append(photo_long)
            photo_accuracy = root[0][i].attrib['accuracy']
            accuracy.append(photo_accuracy)
            photo_context = root[0][i].attrib['context']
            context.append(photo_context)
      print()
      # split data into different packages to stay under 250 (get next packages)---------------------------------------
      if max_taken_date == max_taken_date_input:
            fully_scanned = 1
            print("all data has been fetched \n")
      elif max_taken_date != max_taken_date_input:
            min_taken_date = end_date + timedelta(days=1)
            min_taken_date = min_taken_date.strftime(date_format)
            max_taken_date = max_taken_date_input
            url = 'https://www.flickr.com/services/rest/?method=flickr.photos.search&api_key=f738988d1955a1c8f1e7fcfb981af6b4&tags=wolf&text=wolf&min_upload_date=&max_upload_date=' \
                  + en + urllib.parse.urlencode({'min_taken_date': min_taken_date}) \
                  + en + urllib.parse.urlencode({'max_taken_date': max_taken_date}) \
                  + en + mid_url \
                  + en + urllib.parse.urlencode({'page': page}) \
                  + end_url
            print("new packages url: " + url + "\n")
      # error messages-------------------------------------------------------------------------------------------------
      else:
            print("major error")
print("now out of first while loop")

# place in dataframe (optional)----------------------------------------------------------------------------------------
data_df = pd.DataFrame(
    list(zip(id, owner, secret, title, date_taken, views, tags, machine_tags, lat, long, accuracy, context)),
    columns=['id',
             'owner',
             'secret',
             'title',
             'date_taken',
             'views',
             'tags',
             'machine_tags',
             'latitude',
             'longitude',
             'accuracy',
             'context']
)
# show dataframe as a table (optional)---------------------------------------------------------------------------------
print(tabulate(data_df, headers=["nummer",
                                      "id",
                                      "owner",
                                      "secret",
                                      "date_taken",
                                      "views",
                                      "machine tags",
                                      "latitude",
                                      "longitude",
                                      "accuracy",
                                      "context"], tablefmt='psql'))
print("total items: " + len())
id_check_dublicates = data_df.duplicated()
print(id_check_dublicates)