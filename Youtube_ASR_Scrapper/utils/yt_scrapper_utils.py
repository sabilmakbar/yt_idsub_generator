#to install package from virtual env, cd to {virtualenv_path}/bin
#then do ./python pip install

import time, os, re
import traceback

import subprocess

import selenium
from selenium import webdriver

driver = "firefox"

if driver not in ["firefox", "chrome"]:
    raise ValueError(f"Wrong driver choice! Expected to receive 'firefox' or 'chrome', received {driver}")

if driver == "chrome":
    import webdriver_manager
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
elif driver == "firefox":
    import webdriver_manager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service


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


# A Selenium Spawner
def spawn_driver():

    # # do these lines if anything doesn't work

    # try: #works only on linux, to install chromedriver
    #     install google chrome and its chromedriver
    #     proc_update = subprocess.Popen('sudo apt update')
    #     proc_update.wait()
    #     proc_install = subprocess.Popen('sudo apt install chromium-chromedriver', shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    #     proc_install.wait()
    #     proc_download_gchrome = subprocess.Popen('wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
    #     proc_download_gchrome.wait()
    #     proc_install_gchrome = subprocess.Popen('sudo apt install ./google-chrome-stable_current_amd64.deb')
    #     proc_install_gchrome.wait()

    #     install firefox (much lower RAM usage than chrome, thus less likely for browser to crashed)
    #     proc_install_firefox = subprocess.Popen("wget https://ftp.mozilla.org/pub/firefox/releases/95.0.1/linux-x86_64/en-GB/firefox-95.0.1.tar.bz2")
    #     proc_install_firefox.wait()
    #     # FIREFOX_VERSION="95.0.1"
    #     proc_execute_firefox = subprocess.Popen("tar xvf firefox-95.0.1.tar.bz2")

    # except:
    #     pass


    browser_options = Options()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--disable-dev-shm-usage")
    browser_options.add_argument('--no-sandbox')
    browser_options.add_argument('--disable-gpu')
    # browser_options.add_argument('--incognito')
    browser_options.binary_location = r"/home/jupyter/firefox/firefox"

    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=browser_options)

    return driver


def terminate_chrome_driver(driver: webdriver.Chrome or webdriver.Firefox, action: str="quit"):

    if action not in ["quit", "close"]:
        raise ValueError(f"Action chosen is not one of 'quit' or 'close'! Received value was {action}")

    if action=="quit":
        print("Closing All Browser...")
        driver.quit()
    else:
        print("Closing One Browser...")
        driver.close()


def lazy_load_attribute_crawler(element_list: list, attribute_to_catch: str):
    iterator = iter(element_list)

    print("The total number of videos HTML element identified is: {}".format(len(element_list)))

    while True:
        try:
            attr = (next(iterator)).get_attribute(attribute_to_catch)
        except StopIteration:
            break
        else:
            if attr is not None:
                yield attr


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

    for idx, channel_url in enumerate(channel_urls, start=1):

        #initiate new browser everytime a new channel is created
        driver = spawn_driver()

        channelid = channel_url.split('/')[-2]

        print(f"Retrieving videos list from data number {idx} with channel_id {channelid} from total channel of {len(channel_urls)}")

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

        #create an iterator over web element list
        video_channel_data = driver.find_elements(By.XPATH, '//*[@id="video-title-link"]')

        video_list = list(lazy_load_attribute_crawler(video_channel_data, attribute_to_catch="href"))
        print("The total number of videos obtained is: {}".format(len(video_list)))

        video_list_output.append({"channel_url":channel_url, "public_video_list": video_list})

        #close the window everytime a link scraping is finished from a channel URL
        terminate_chrome_driver(driver)

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
        await session.close()
        raise
    except:
        print("An error occurred when trying to get URL response!")
        print(''.join(traceback.format_stack()))
        await session.close()
        raise

    # execute Java-script
    try:
        await response.html.arender(sleep=1, timeout = timeout)
    except TimeoutError as Te:
        print(Te[:-1]+", need to increase default timeout or retry again")
        await session.close()
        raise
    except:
        print("An error occurred when trying to render HTML!")
        print(''.join(traceback.format_stack()))
        await session.close()
        raise

    # create bs object to parse HTML
    soup = bs(response.html.raw_html, "html.parser")

    try:
        upload_date = soup.find("meta", itemprop="uploadDate")['content']
        duration = soup.find("span", {"class": "ytp-time-duration"}).text
        vid_title = soup.find("meta", itemprop="name")["content"]
    except (TypeError, AttributeError) as e:
        print(f"Informations unavailable when doing BS find! Message: {e}")
        raise
    except:
        print(f"An error occurred when parsing the BS!")
        print(''.join(traceback.format_stack()))
        raise
    finally:
        await session.close()

    if not re.match("^\d{1,}(:\d{2}){,2}(:\d{2})$", duration):
        print(f"The duration info pattern is unexpected! Received str: {duration}")
        duration_s = None
    else:
        ts_measured = [86400,3600,60,1]
        duration_reversed = list(map(int,duration.split(":")[::-1]))
        ts_reversed_used = ts_measured[::-1][:len(duration_reversed)]
        duration_s = sum([a*b for a,b in zip(ts_reversed_used, duration_reversed)])


    # get the metadata dict
    output_dict = {"title": vid_title,
                   "duration": duration,
                   "duration_s": duration_s,
                   "upload_date": upload_date}

    return output_dict


def yt_metadata_scrapper(video_urls: list, timeout: int = 60):
    """Retrieving a dict of metadata from YT URL input using asyncronous method
    input:
        channel_url (list of str) -- an list of url links of input video to be retrieved of its metadata
        timeout (int, optional) -- a timeout variable for waiting response
    output: output_dict (dict) -- a dict of metadata, which can be found on function "async_yt_metadata_scrapper"
    """

    result_list = []
    for video_url in video_urls:
        output = asyncio.run(async_yt_metadata_scrapper(video_url, timeout))
        try:
            output.keys()
        except:
            print(f"Exception occured in 'async_yt_metadata_scrapper' function! Skipping the value for now...")
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
