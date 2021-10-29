import numpy as np
import youtube_dl
import csv
import urllib
import urllib.request
import re
import unidecode
from tqdm import tqdm
import pytube
import pandas as pd
from pytube import YouTube

inputfile = csv.reader(open('../data/unesco_sites_cleaned.csv','r'), delimiter=';')

ydl_opts = {
'format': 'bestaudio/best',
'outtmpl': 'tmp/%(id)s.%(ext)s',
'noplaylist': True,
'quiet': True,
'prefer_ffmpeg': True,
'audioformat': 'wav',
'forceduration':True
}

# create an empty dictionnary
video_dict = {}


# read line by line
for row in tqdm(inputfile):
    
    # get second column (names of places)
    place = row[1]
    
    # clean string : remove accents
    place_clean1 = unidecode.unidecode(place)
    # clean string : remove spaces
    place_clean2 = place_clean1.replace(' ', '+')
    
    # add key words 
    search_words = place_clean2 + "+drone"
    
    # make a request in youtube, store the results in a list
    results = []
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_words)
    
    # store the results
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
  
    for video_id in video_ids:
        try:
            ydl_opts = {'ignoreerrors': True}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                myVideo = YouTube("https://www.youtube.com/watch?v=%s" % video_id)
                if (myVideo.streams.filter(res="2160p") != None) :
                    if not myVideo.age_restricted:
                        dictMeta = ydl.extract_info("https://www.youtube.com/watch?v=%s" % video_id, download=False)
            
                        video_dict.update({video_id : [place_clean1, dictMeta['duration'], dictMeta['title'], dictMeta['upload_date']]})
            
        except Exception as e:
            print("ERROR Catched and Passed", e)
            pass 
        
    
video_df = pd.DataFrame.from_dict(video_dict, orient='index', columns=['place', 'duration', 'title', 'date'])

video_df.to_csv('../data/video_info.csv', index_label = 'id')
