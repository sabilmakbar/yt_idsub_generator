#to install package from virtual env, cd to {virtualenv_path}/bin
#then do ./python pip install

import time, os, re

from selenium import webdriver
import subprocess

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup as bs #importing BeautifulSoup

import asyncio
import nest_asyncio

import yt_dlp

#pip install webvtt-py (to get package webvtt)
import webvtt
import pandas as pd
import numpy as np


# A Python Selenium Scraper for Retrieve the List of Links from A Channel
def channel_video_link_scrapper(channel_urls: list, wait_time_load: int=10, wait_time_scroll: int=3):
    """Retrieving a list of all public videos in the given channel URL
    input:
        >> channel_urls (list of str) -- an url link of input channel to be scraped, has to be a "video" tab link
        >> wait_time_load (int, optional) -- params to set selenium wait (or sleep) to load that URL, default to 10s
        >> wait_time_scroll (int, optional) -- params to set selenium wait (or sleep) to load that URL, default to 3s
    output: video_list (dict) -- a dict of input + all public videos uploaded in that channel
    Reference: https://github.com/banhao/scrape-youtube-channel-videos-url/blob/master/scrape-youtube-channel-videos-url.py
    """

    #Assert all inputs are youtube link
    for url in channel_urls:
        if "youtube.com" not in url:
            raise ValueError("This string 'youtube.com' is not in {}, it's not a default YT link!".format(url))
        if not(url.split('/')[-1] == "videos"):
            raise ValueError("The url {} is not a valid YT Channel URL that contains all videos!".format(channel_url))

    video_list_output = []

    try: #works only on linux, to install chromedriver
        proc_update = subprocess.Popen('sudo apt update')
        proc_update.wait()
        proc_install = subprocess.Popen('sudo apt install chromium-chromedriver', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        proc_install.wait()
        proc_download_gchrome = subprocess.Popen('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
        proc_download_gchrome.wait()
        proc_install_gchrome = subprocess.Popen('sudo apt install ./google-chrome-stable_current_amd64.deb')
        proc_install_gchrome.wait()
    except:
        pass

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for idx, channel_url in enumerate(channel_urls, start=1):
        channelid = channel_url.split('/')[-2]

        print(f"Retrieving videos list from data number {idx} with channel_id {channelid}")

        driver.get(channel_url)
        time.sleep(wait_time_load)
        height = driver.execute_script("return document.documentElement.scrollHeight")
        lastheight = 0

        while True:
            if lastheight == height:
                break
            lastheight = height
            driver.execute_script("window.scrollTo(0, " + str(height) + ");")
            time.sleep(wait_time_scroll)
            height = driver.execute_script("return document.documentElement.scrollHeight")

        time.sleep(wait_time_load)
        user_data = driver.find_elements(By.XPATH, '//*[@id="video-title-link"]')

        print("The total number of videos HTML element identified from channel id {} is: {}".format(channelid, len(user_data)))

        video_list = [data.get_attribute("href") for data in user_data if data.get_attribute("href") is not None]

        print("The total number of videos obtained from channel id {} is: {}".format(channelid, len(video_list)))

        video_list_output.append({"channel_url":channel_url, "public_video_list": video_list})

    #close the window
    driver.quit()

    return {"data": video_list_output}


# A Python Metadata Collection for Retrieve the Video Duration
async def async_yt_metadata_scrapper(*args, shorts_identifier = "/shorts/"):
    """Async Method for Retrieving metadata of given public videos.
    Has to be called within function "yt_metadata_scrapper" to make the output works
    as intended.
    It follows the input from "yt_metadata_scrapper"
    Reference: https://www.thepythoncode.com/article/get-youtube-data-python
    """

    video_url, timeout = args

    if shorts_identifier in video_url:
        print("YT Shorts link detected: {}.".format(video_url))
        return {"title": False, "duration": False,
                "duration_s": False, "upload_date": False}

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
        print(f"Video duration: {duration}")
        print(f"Video name: {vid_title}")

    except (TypeError, AttributeError) as e:
        print("Informations unavailable!")
        return None

    if not re.match("^\d{1,2}(:\d{2}){,2}$", duration):
        print("Warning, the duration info is invalid or > 1day. Returning duration_s variable as None!")
        duration_s = None
    else:
        duration_splitted = duration.split(":")
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


async def async_yt_list_metadata_scrapper(*args):
    video_urls, timeout = args
    return await asyncio.gather(*[async_yt_metadata_scrapper(video_url, timeout) for video_url in video_urls])


def yt_metadata_scrapper(video_urls: list, timeout: int = 60):
    """Retrieving a dict of metadata from YT URL input using asyncronous method
    input:
        channel_url (list of str) -- an list of url links of input video to be retrieved of its metadata
        timeout (int, optional) -- a timeout variable for waiting response
    output: output_dict (dict) -- a dict of metadata, which can be found on function "async_yt_metadata_scrapper"
    """

    if asyncio.get_event_loop().is_running(): # Only patch if needed (i.e. running in Notebook, Spyder, etc)
        nest_asyncio.apply()

    result_list = []
    for video_url in video_urls:
        output = asyncio.run(async_yt_metadata_scrapper(video_url, timeout))
        try:
            output.keys()
        except AttributeError as e: #the result is None
            result_list.append(None)
        else:
            result_list.append({"video_url": video_url, "meta": output})


    output_dict = {"data": result_list}

    return output_dict


#unpack video_meta output from dict to df
def video_meta_retriever(value_to_retrieve: dict):
    """Cast A Misparsed Object from String to its Original Object
    input: value_to_retrieve (str) -- value to be converted
    output: retrieved_value (object from ast_literal result, or None if ValueError) -- returned value
    """

    try:
        retrieved_value = (value_to_retrieve["meta"]["title"],
                            value_to_retrieve["meta"]["duration_s"],
                            value_to_retrieve["meta"]["upload_date"])
    except TypeError as e:
        print(e)
        retrieved_value = (None, None, None)

    return retrieved_value


def yt_subtitle_downloader(video_urls: list, folder_path_to_save: str = os.getcwd(), ydl_opts : dict=None, lang: str="id"):
    """
    This function will download the subtitle file of the video(s) from the input list of youtube links,
    and save it in the specified folder path

    input:
        video_urls (list): list of youtube video links
        folder_path_to_save (str): The folder path where you want to save the subtitles
        ydl_opts (dict): a dictionary of options to pass to the downloader
        lang (str, optional): the language of the subtitles you want to download, default to "id" (Indonesian)
    output:
        None (a file of format .vtt)
    """

    #check if "youtube.com" contains in the list input
    for url in video_urls:
        if "youtube.com" not in url:
            raise ValueError("This string 'youtube.com' is not in {}, it's not a default YT link!".format(url))

    if not os.path.isdir(folder_path_to_save):
        os.mkdir(folder_path_to_save)

    print(f"Saving subtitle to: {folder_path_to_save}")

    #reference on outtmpl: https://stackoverflow.com/questions/32482230/how-to-set-up-default-download-location-in-youtube-dl/34958672
    #check on subtitles availability: yt-dlp --list-subs {any_video_links}
    if ydl_opts is None:
        ydl_opts = {
            'format': 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4] / wv*+ba/w', #Ensures best settings
            'writesubtitles': True, #Adds a subtitles file if it exists
            'writeautomaticsub': True, #Adds auto-generated subtitles file
            'subtitleslangs' : [lang], #set the default lang for subtitle (or auto-subtitle)
            'skip_download': True, #skips downloading the video file, if we want to download the vid just change into false
            'outtmpl': os.path.join(folder_path_to_save, '%(id)s.%(ext)s')
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
        subtitle_data = webvtt.read(os.path.join(saved_folder_path,file))

        #Create dataframe of subtitle filled with start and stop time, and also the text
        text_time = pd.DataFrame()
        text_time['text'] = [data.text for data in subtitle_data]
        text_time['start'] = [data.start for data in subtitle_data]
        text_time['stop'] = [data.end for data in subtitle_data]
        text_time['link'] = "https://www.youtube.com/watch?v=" + file.strip(".vtt")

        #Replace duplicate values that was indicated by /n
        text_time['text'] = text_time['text'].str.split('\n').str.get(-1)
        text_time = text_time.replace(r'^\s*$', np.nan, regex=True).dropna()

        #convert to csv
        text_time.to_csv('{}/{}.csv'.format(saved_folder_path, file[:-7].replace(" ","")),index=False) #-7 to remove '.{2char_language_vtt_filename}.vtt'

        #remove files from local drive
        os.remove(os.path.join(saved_folder_path,file))
