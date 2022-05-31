# Created by Maarten De Nocker on 14/11/2021
# Tool to get data from Flickr API

import urllib.parse
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
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
latitude = []
longitude = []
accuracy = []
context = []

# ask for api key + criteria-------------------------------------------------------------------------------------------

 # ask for api key-----------------------------------------------------------------------------------------------------
line = "-" * 35
print(line)
if os.path.exists("api-key.txt") == True:
    while True:
        answer = str(input("Do you want to use a saved api key(Y/N): "))
        if answer == 'y' or answer == 'Y':
            print("Opening api key")
            f = open("api-key.txt", "r")
            api_key = f.read()
            print("Api key is: " + api_key)
            f.close()
            break
        elif answer == 'n' or answer == 'N':
            api_key = str(input("Enter your api key\n"
                                "you can get your api key from https://www.flickr.com/services/apps/create/\n"
                                ": "))
            answer = str(input("Do you want to save this api key(Y/N): "))
            while True:
                if answer == 'y' or answer == 'Y':
                    print("Saving api key")
                    f = open("api-key.txt", "w")
                    f.write(api_key)
                    f.close()
                    break
                elif answer == 'n' or answer == 'N':
                    break
                else:
                    print("Please give one of the above specified answer")
            break
        else:
            print("Please give one of the above specified answer")
else:
    api_key = str(input("Enter your api key\n"
                    "your can get your api key from https://www.flickr.com/services/apps/create/\n"
                    ": "))
    answer = str(input("Do you want to save this api key(Y/N): "))
    while True:
        if answer == 'y' or answer == 'Y':
            print("Saving api key")
            f = open("api-key.txt", "w")
            f.write(api_key)
            f.close()
            break
        elif answer == 'n' or answer == 'N':
            break
        else:
            print("Please give one of the above specified answer")

 # ask for criteria----------------------------------------------------------------------------------------------------
print('Enter your criteria. If you leave a place blank it will be skipped')
# implement feature for multiple tags and excluding tags
while True:
    try:
        tag = str(input("Enter tag: "))
        text = str(input("Enter text: "))
        chose = input("Do you want to add any date regarding criteria(Y/N): ")
        if chose == 'y' or chose == 'Y':
            min_upload_date = str(input("Enter the minimum upload date (format: yyyy-mm-dd): "))
            max_upload_date = str(input("Enter the maximum upload date (format: yyyy-mm-dd): "))
            min_taken_date = str(input("Enter the minimum taken date (format: yyyy-mm-dd): "))
            max_taken_date = str(input("Enter the maximum taken date (format: yyyy-mm-dd): "))
        elif chose == 'n' or chose == 'N' or chose =='':
            print("No date criteria will be used")
            min_upload_date = ""
            max_upload_date = ""
            min_taken_date = ""
            max_taken_date = ""
        else:
            raise Exception
        while True:
            if min_taken_date == "" or max_taken_date == "":
                print("Your are OBLIGATED to add a minimum and maximum date for when the picture is taken")
                min_taken_date = str(input("Enter the minimum taken date (format: yyyy-mm-dd): "))
                max_taken_date = str(input("Enter the maximum taken date (format: yyyy-mm-dd): "))
            else:
                break
        min_taken_date_input = min_taken_date # to have original inputs for later
        max_taken_date_input = max_taken_date
        safe_search = str(input("Enter the safe search factor"
                                "\n1 for safe"
                                "\n2 for moderate"
                                "\n3 for restricted"
                                "\n : "))
        if safe_search != '1' and safe_search != '2' and safe_search != '3' and safe_search != '':
            raise Exception
        woe_id = '' # doesn't currently work
        media = str(input("Enter the type of media (all, photos, videos): "))
        if media != 'all' and media != 'photos' and media != 'videos' and media != '':
            raise Exception
        has_geo = '' # doesn't currently work
        geo_context = str(input("Do you want the photos to have location context"
                                "\n0 for not defined"
                                "\n1 for indoors"
                                "\n2 for outdoors"
                                "\n : "))
        if geo_context != '0' and geo_context != '1' and geo_context != '2' and geo_context != '':
            raise Exception
        lat = input("Enter the latitude (in decimal format): ")
        exception = 0
        try:
            lat = int(lat)
        except:
            exception = 1
        if exception == 1 and lat != '':
            raise Exception
        lat = str(lat)
        lon = input("Enter the longitude (in decimal format): ")
        exception = 0
        try:
            lon = int(lon)
        except:
            exception = 1
        if exception == 1 and lon != '':
            raise Exception
        lon = str(lon)
        radius = input("Enter the radius around the above entered point"
                           "\n(in kilometers, greater than 0, less than 32): ")
        exception = 0
        try:
            radius = int(radius)
            if radius < 1 or radius > 31:
                raise Exception
        except:
            exception = 1
        if exception == 1 and radius != '':
            raise Exception
        radius = str(radius)
        radius_units = 'km'
        per_page = '250' # flickr documentation says 500 is the maximum, but your page will than be split into to 2
        page = '1'
        print()
    except:
        print("Please chose between the given options or only use whole numbers")
        print()
        continue
    else:
        break

# getting data---------------------------------------------------------------------------------------------------------

# making main url-----------------------------------------------------------------------------------------------------
main_api = 'https://www.flickr.com/services/rest/?method=flickr.photos.search'
en = '&'
end_url = '&sort=date-taken-asc&extras=geo,date_taken,tags,machine_tags,description,views&format=rest'
begin_url = main_api\
            + en + urllib.parse.urlencode({'api_key': api_key})\
            + en + urllib.parse.urlencode({'tags': tag})\
            + en + urllib.parse.urlencode({'text': text})\
            + en + urllib.parse.urlencode({'min_upload_date': min_upload_date})\
            + en + urllib.parse.urlencode({'max_upload_date': max_upload_date})\
            + en + urllib.parse.urlencode({'safe_search': safe_search})\
            + en + urllib.parse.urlencode({'woe_id': woe_id})\
            + en + urllib.parse.urlencode({'media': media})\
            + en + urllib.parse.urlencode({'has_geo': has_geo})\
            + en + urllib.parse.urlencode({'geo_context': geo_context})\
            + en + urllib.parse.urlencode({'lat': lat})\
            + en + urllib.parse.urlencode({'lon': lon})\
            + en + urllib.parse.urlencode({'radius': radius})\
            + en + urllib.parse.urlencode({'radius_units': radius_units})\
            + en + urllib.parse.urlencode({'per_page': per_page})\
            + en + urllib.parse.urlencode({'page': page})\
            + end_url
url = begin_url\
      + en + urllib.parse.urlencode({'min_taken_date': min_taken_date})\
      + en + urllib.parse.urlencode({'max_taken_date': max_taken_date})
print("Getting data from:")
print(url)

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
            url = begin_url \
                  + en + urllib.parse.urlencode({'min_taken_date': min_taken_date}) \
                  + en + urllib.parse.urlencode({'max_taken_date': max_taken_date})
            print("new url: " + url)
            xml_data = requests.get(url)
            parser = ET.XMLParser(encoding="utf-8")
            root = ET.fromstringlist(xml_data, parser=parser)
            total = int(root[0].attrib['total'])
            print()
      # get data from this packages into lists-------------------------------------------------------------------------
      print("total items in package: " + str(total))
      i = 0
      while True:
          try:
              print(root[0][i].attrib['id'])
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
              photo_datetaken = photo_datetaken[:-9]
              date_taken.append(photo_datetaken)
              photo_views = root[0][i].attrib['views']
              views.append(photo_views)
              photo_tags = root[0][i].attrib['tags']
              tags.append(photo_tags)
              photo_machine_tags = root[0][i].attrib['machine_tags']
              machine_tags.append(photo_machine_tags)
              photo_lat = root[0][i].attrib['latitude']
              latitude.append(photo_lat)
              photo_long = root[0][i].attrib['longitude']
              longitude.append(photo_long)
              photo_accuracy = root[0][i].attrib['accuracy']
              accuracy.append(photo_accuracy)
              photo_context = root[0][i].attrib['context']
              context.append(photo_context)
              i += 1
          except:
              break
      print()
      # split data into different packages to stay under 250 (get next packages)---------------------------------------
      if max_taken_date == max_taken_date_input:
            fully_scanned = 1
            print("all data has been fetched \n")
      elif max_taken_date != max_taken_date_input:
            min_taken_date = end_date + timedelta(days=1)
            min_taken_date = min_taken_date.strftime(date_format)
            max_taken_date = max_taken_date_input
            url = begin_url \
                  + en + urllib.parse.urlencode({'min_taken_date': min_taken_date}) \
                  + en + urllib.parse.urlencode({'max_taken_date': max_taken_date})
            print("new packages url: " + url + "\n")
      # error messages-------------------------------------------------------------------------------------------------
      else:
            print("major error")
print("now out of first while loop")

# place in dataframe (optional)----------------------------------------------------------------------------------------
data_df = pd.DataFrame(
    list(zip(id, owner, secret, title, date_taken, views, tags, machine_tags, latitude, longitude, accuracy, context)),
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