# -*- coding: utf-8 -*-
"""youtube_download.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JUfrUYj7W30v4X42il7Dxiyl7PMsKZaU
"""

#Download module to your Colab
!pip install yt-dlp
!pip install webvtt-py

from __future__ import unicode_literals
import yt_dlp

yt_url = ['https://www.youtube.com/watch?v=5hEeDh5hoPQ&list=PLd5Z1CCkFEeZv6bj-cBTxWXOy8SN_oLSS']

ydl_opts = {
'format': 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4] / wv*+ba/w', #Ensures 480p and mp4 output
'writesubtitles': True, #Adds a subtitles file if it exists
'writeautomaticsub': True, #Adds auto-generated subtitles file
'subtitle': '--sub-lang en', #writes subtitles file in english
#'subtitlesformat':'srt', #writes the subtitles file in "srt" or "ass/srt/best"
'skip_download': True, #skips downloading the video file, if we want to download the vid just change into false
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
  ydl.download(yt_url)
print("Download Successful!")

import webvtt
import pandas as pd
import os
import numpy as np

filenames_vtt = [os.fsdecode(file) for file in os.listdir(os.getcwd()) if os.fsdecode(file).endswith(".vtt")]

def convert_vtt(filenames):    
    #create an assets folder if one does not yet exist
    if os.path.isdir('{}/assets'.format(os.getcwd())) == False:
        os.makedirs('assets')
    #extract the text and times from the vtt file
    for file in filenames:
        captions = webvtt.read(file)
        text_time = pd.DataFrame()
        text_time['text'] = [caption.text for caption in captions]
        text_time['start'] = [caption.start for caption in captions]
        text_time['stop'] = [caption.end for caption in captions]

        text_time['text'] = text_time['text'].str.split('\n').str.get(-1)
        text_time = text_time.replace(r'^\s*$', np.nan, regex=True).dropna()

        text_time.to_csv('assets/{}.csv'.format(file[:-7]),index=False) #-7 to remove '.en.vtt'
        #remove files from local drive
        os.remove(file)

#call the function
convert_vtt(filenames_vtt)

csv_files = [os.fsdecode(file) for file in os.listdir(os.getcwd()+'/assets') if os.fsdecode(file).endswith('.csv')]
path = 'assets/'

def neat_csv(filecsv):
  for filename in csv_files:
    os.rename(os.path.join(path, filename), os.path.join(path, filename.replace(' ', ''))) #get rid of the white space
  
  clean_csv = [os.fsdecode(file) for file in os.listdir(os.getcwd()+'/assets')]

  #extract the text and videoid
  vidText = []
  csv_vidid = []

  for file in clean_csv:
    df = pd.read_csv(path+file)
    text = df.text.to_list()
    vidText.append(text)
    csv_vidid.append(file[-18:-7])

  vid_df = pd.DataFrame()
  vid_df['vid_title'] = clean_csv
  vid_df['vid_text'] = vidText
  vid_df['vid_id'] = csv_vidid

  return vid_df

shark_tank = neat_csv(csv_files)
shark_tank.head()