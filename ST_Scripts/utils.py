#to install package from virtual env, cd to {virtualenv_path}/bin 
#then do ./python pip install 

import time, datetime, os

import urllib.request, urllib.error, urllib.parse

from selenium import webdriver
import subprocess

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options


from requests_html import AsyncHTMLSession 
from bs4 import BeautifulSoup as bs # importing BeautifulSoup

import asyncio
import nest_asyncio

import yt_dlp

#pip install webvtt-py (to get package webvtt)
import webvtt
import pandas as pd
import numpy as np


# A Python Selenium Scraper for Retrieve the List of Links from A Channel
def channel_video_link_scraper(channel_urls: list):
    """Retrieving a list of all public videos in the given channel URL
    input: channel_urls (list of str) -- an url link of input channel to be scraped, has to be a "video" tab link
    output: video_list (dict) -- a dict of input + all public videos uploaded in that channel 
    Reference: https://github.com/banhao/scrape-youtube-channel-videos-url/blob/master/scrape-youtube-channel-videos-url.py
    """

    try: #works only on linux, to install chromedriver
        proc = subprocess.Popen('apt install chromium-chromedriver', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        proc.wait()
    except:
        pass

    #Assert all inputs are youtube link
    for url in channel_urls:
        if "youtube.com" not in url:
            raise ValueError("This string 'youtube.com' is not in {}, it's not a default YT link!".format(url))
        if not(url.split('/')[-1] == "videos"):        
            raise ValueError("The url {} is not a valid YT Channel URL that contains all videos!".format(channel_url))

    video_list_output = []

    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome-data")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    for idx, channel_url in enumerate(channel_urls, start=1):
        channelid = channel_url.split('/')[-2]

        print(f"Retrieving videos list from data number {idx} with channel_id {channelid}")

        driver.get(channel_url)
        time.sleep(5)
        height = driver.execute_script("return document.documentElement.scrollHeight")
        lastheight = 0

        while True:
            if lastheight == height:
                break
            lastheight = height
            driver.execute_script("window.scrollTo(0, " + str(height) + ");")
            time.sleep(2)
            height = driver.execute_script("return document.documentElement.scrollHeight")

        user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
        
        print("The total number of videos catched from channel id {} is: {}".format(channelid, len(user_data)))

        video_list = [data.get_attribute('href') for data in user_data]
        video_list_output.append({"channel_url":channel_url, "public_video_list": video_list})
    
    return {"data": video_list_output}


# A Python Metadata Collection for Retrieve the Video Duration
async def async_yt_metadata_scraper(*args, shorts_identifier = "/shorts/"):
    """Async Method for Retrieving metadata of given public videos.
    Has to be called within function "yt_metadata_scraper" to make the output works
    as intended.
    It follows the input from "yt_metadata_scraper"
    Reference: https://www.thepythoncode.com/article/get-youtube-data-python
    """

    video_url, timeout = args

    if shorts_identifier in video_url:
        print("YT Shorts link detected: {}.".format(video_url))
        return None
    
    print("Executing YT Metadata Scraper for link {}.".format(video_url))

    # init an HTML Session
    session = AsyncHTMLSession()
    # get the html content
    try:
        response = await session.get(video_url)
    except TimeoutError as Te:
        print(Te[:-1]+", need to increase default timeout or retry again")
        return None
    except Exception as e:
        print(e)
        return None

    # execute Java-script
    try:
        await response.html.arender(sleep=1, timeout = timeout)
    except TimeoutError as Te:
        print(Te[:-1]+", need to increase default timeout or retry again")
        await session.close()
        return None
    except Exception as e:
        print(e)
        await session.close()
        return None

    # create bs object to parse HTML
    soup = bs(response.html.raw_html, "html.parser")

    try:
        upload_date = soup.find("meta", itemprop="uploadDate")['content']
        duration = soup.find("span", {"class": "ytp-time-duration"}).text
        vid_title = soup.find("meta", itemprop="name")["content"]
        print("Informations available!.")

        print(f"Upload date: {upload_date}")
        print(f"Upload date: {duration}")
        print(f"Upload date: {vid_title}")

    except (TypeError, AttributeError) as e:
        print("Informations unavailable!")
        return None
    
    duration_splitted = duration.split(":")
    if len(duration_splitted) > 3:
        print("Warning, the duration is >24 h. Returning duration_s variable as None!")
        duration_s = None
    elif duration_splitted == "":
        print("Warning, the duration info is invalid. Returning duration_s variable as None!")
        duration_s = None
    else:
        duration_s = int(duration_splitted[-1])
        try:
            duration_s += int(duration_splitted[-2])*60
        except:
            pass
        else:
            try:
                duration_s += int(duration_splitted[-3])*3600
            except:
                pass
    
    await session.close()
    
    # get the metadata dict
    output_dict = {"title": vid_title,
                   "duration": duration,
                   "duration_s": duration_s,
                   "upload_date": upload_date}

    return output_dict


async def async_yt_list_metadata_scraper(*args):
    video_urls, timeout = args
    return await asyncio.gather(*[async_yt_metadata_scraper(video_url, timeout) for video_url in video_urls])


def yt_metadata_scraper(video_urls: list, timeout: int = 60):
    """Retrieving a dict of metadata from YT URL input using asyncronous method
    input: 
        channel_url (list of str) -- an list of url links of input video to be retrieved of its metadata
        timeout (int, optional) -- a timeout variable for waiting response
    output: output_dict (dict) -- a dict of metadata, which can be found on function "async_yt_metadata_scraper"
    """

    if asyncio.get_event_loop().is_running(): # Only patch if needed (i.e. running in Notebook, Spyder, etc)
        nest_asyncio.apply()

    result_list = []
    for video_url in video_urls:
        result_list.append({"video_url": video_url, "meta": asyncio.run(async_yt_metadata_scraper(video_url, timeout))})
    
    # #async version, but doesn't work bcs of runtime issue
    # result_list = asyncio.run(async_yt_list_metadata_scraper(video_urls, timeout))
    
    output_dict = {"data": result_list}
    return output_dict


def yt_subtitle_downloader(video_urls: list, folder_path_to_save: str = os.getcwd(), ydl_opts : dict=None):
    """Retrieving subtitle info and timestamp from YT URL input.
    It will save the downloaded files into "path_to_save" variables.
    It is recommended to fill in folder_path_to_save rather than leave it as default.
    input: 
        channel_url (list of str) -- a list of url links of input video to be scraped
        path_to_save (str, optional) -- a path for storing result (defaults to current working directory)
    """

    #check if "youtube.com" contains in the list input
    for url in video_urls:
        if "youtube.com" not in url:
            raise ValueError("This string 'youtube.com' is not in {}, it's not a default YT link!".format(url))
    
    #reference on outtmpl: https://stackoverflow.com/questions/32482230/how-to-set-up-default-download-location-in-youtube-dl/34958672
    if ydl_opts is None:
        ydl_opts = {
            'format': 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4] / wv*+ba/w', #Ensures best settings
            'writesubtitles': True, #Adds a subtitles file if it exists
            'writeautomaticsub': True, #Adds auto-generated subtitles file
            'subtitle': '--sub-lang en', #writes subtitles file in english
            'skip_download': True, #skips downloading the video file, if we want to download the vid just change into false
            'outtmpl': folder_path_to_save + '/%(title)s.%(ext)s'
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_urls)


def yt_subtitle_file_vtt_to_csv_converter(saved_folder_path: str = os.getcwd()):
    """Changing and parsing all file from vtt format (yt-dl download file) to csv.
    It will check all .vtt files from "saved_folder_path" variables,
    then parse and reformat it into dataframe csv format and delete the .vtt file.
    input: 
        channel_url (list of str) -- a list of url links of input video to be scraped
        path_to_save (str, optional) -- a path for storing result (defaults to current working directory)
    """

    filenames = [file for file in os.listdir(saved_folder_path) if os.fsdecode(file).endswith(".vtt")]

    #Extract the text and times from the vtt file
    for file in filenames:
        captions = webvtt.read(os.path.join(saved_folder_path,file))

        #Create dataframe of subtitle filled with start and stop time, and also the text
        text_time = pd.DataFrame()
        text_time['text'] = [caption.text for caption in captions]
        text_time['start'] = [caption.start for caption in captions]
        text_time['stop'] = [caption.end for caption in captions]

        #Replace duplicate values that was indicated by /n
        text_time['text'] = text_time['text'].str.split('\n').str.get(-1)
        text_time = text_time.replace(r'^\s*$', np.nan, regex=True).dropna()

        #convert to csv
        text_time.to_csv('{}/{}.csv'.format(saved_folder_path, file[:-7].replace(" ","")),index=False) #-7 to remove '.en.vtt'
        #remove files from local drive
        os.remove(os.path.join(saved_folder_path,file))
