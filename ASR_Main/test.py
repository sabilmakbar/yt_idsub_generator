# %%
from requests_html import AsyncHTMLSession, HTMLSession

from bs4 import BeautifulSoup as bs #importing BeautifulSoup

import re, sys
import threading
import traceback

import asyncio
# import nest_asyncio


# async def _get_html_yt_metadata(*args, shorts_identifier = "/shorts/", sleep_timer: int=0.7):
#     """Async Method for Retrieving metadata of given public videos.
#     Has to be called within function "yt_metadata_scrapper" to make the output works
#     as intended.
#     It follows the input from "yt_metadata_scrapper"
#     Reference: https://www.thepythoncode.com/article/get-youtube-data-python
#     """

#     default_timeout = 60

#     try:
#         video_url, timeout, *_ = args
#     except ValueError as ve:
#         if "not enough values to unpack (expected at least 2, got 1)" in str(ve):
#             video_url = args[0]
#             timeout = default_timeout
#             print(f"Received only 1 arg! Setting timeout to default timeout of {default_timeout}...")
#         else:
#             print("Unmatched args number! Expected only 2 args unpacked, received 0!")
#             raise

#     if shorts_identifier in video_url:
#         print("YT Shorts link detected: {}.".format(video_url))
#         raise ValueError("Unexpected YT Short Link received!")

#     print("Executing YT Metadata Scraper for link {}.".format(video_url))

#     # init an HTML Session
#     with AsyncHTMLSession() as asession:
#         # get the html content
#         try:
#             response = await asession.get(video_url)
#         except TimeoutError as Te:
#             print(Te[:-1]+", need to increase default timeout or retry again.")
#             await asession.close()
#             raise
#         except:
#             print("An error occurred when trying to get URL response!")
#             print(''.join(traceback.format_stack()))
#             await asession.close()
#             raise
#         else:
#             # execute Java-script
#             try:
#                 await response.html.arender(sleep=sleep_timer, timeout = timeout)
#             except TimeoutError as Te:
#                 print(Te[:-1]+", need to increase default timeout or retry again")
#                 await asession.close()
#                 raise
#             except:
#                 print("An error occurred when trying to render HTML!")
#                 print(''.join(traceback.format_stack()))
#                 await asession.close()
#                 raise
#             else:
#                 await asession.close()
#                 return response.html.raw_html


# class RunThread(threading.Thread):
#     def __init__(self, func, args, kwargs):
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#         self.result = None
#         super().__init__()

#     def run(self):
#         self.result = asyncio.run(self.func(*self.args, **self.kwargs))


# def run_async(func, *args, **kwargs):
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         print("No running loop...")
#         loop = None
#     if loop and loop.is_running():
#         print("Create New Thread")
#         thread = RunThread(func, args, kwargs)
#         thread.start()
#         thread.join()
#         return thread.result
#     else:
#         print("Using Main Thread")
#         return asyncio.run(func(*args, **kwargs))


# def _singular_parse_html_using_bs(html_raw):
#     # create bs object to parse HTML
#     soup = bs(html_raw, "html.parser")

#     try:
#         upload_date = soup.find("meta", itemprop="uploadDate")['content']
#         duration = soup.find("span", {"class": "ytp-time-duration"}).text
#         vid_title = soup.find("meta", itemprop="name")["content"]
#     except (TypeError, AttributeError) as e:
#         print(f"Informations unavailable when doing BS find! Message: {e}")
#         raise
#     except:
#         print(f"An error occurred when parsing the BS!")
#         print(f"Details: \n{traceback.print_stack()}")
#         raise

#     if not re.match("^\d{1,}(:\d{2}){,2}(:\d{2})$", duration):
#         print(f"The duration info pattern is unexpected! Received str: {duration}")
#         duration_s = None
#     else:
#         ts_measured = [86400,3600,60,1]
#         duration_reversed = list(map(int,duration.split(":")[::-1]))
#         ts_reversed_used = ts_measured[::-1][:len(duration_reversed)]
#         duration_s = sum([a*b for a,b in zip(ts_reversed_used, duration_reversed)])

#     # get the metadata dict
#     output_dict = {"title": vid_title,
#                    "duration": duration,
#                    "duration_s": duration_s,
#                    "upload_date": upload_date}

#     return output_dict


# def _list_parse_html_using_bs(html_list: list):
#     result_list = list()
#     for idx, html in enumerate(html_list):
#         try:
#             html
#         except:
#             print(f"Exception occured in 'async_yt_metadata_scrapper'! Skipping the value for now...")
#             print(f"Skipping input no: {idx+1}")
#             print(f"Details: \n{traceback.print_stack()}")
#             result_list.append(None)
#         else:
#             try:
#                 _singular_parse_html_using_bs(html)
#             except:
#                 print(f"Exception occured in '_parse_html_using_bs'! Skipping the value for now...")
#                 print(f"Skipping input no: {idx+1}")
#                 print(f"Details: \n{traceback.print_stack()}")
#                 result_list.append(None)
#             else:
#                 result_list.append(_singular_parse_html_using_bs(html))
    
#     return result_list

# from concurrent.futures import ThreadPoolExecutor


# _executor = ThreadPoolExecutor(1)

# async def _yt_metadata_scrapper(*args):

#     default_timeout = 60

#     try:
#         video_url_list, timeout, *_ = args
#     except ValueError as ve:
#         if "(expected 2)" in ve:
#             video_url_list = args[0]
#             timeout = default_timeout
#             print(f"Received only 1 arg! Setting timeout to default timeout of {default_timeout}...")
#         else:
#             print("Unmatched args number! Expected only 2 args unpacked, received 0!")

#     html_list = await asyncio.gather(*[(_get_html_yt_metadata(video_url, timeout)) for video_url in video_url_list], return_exceptions=True)

#     loop = asyncio.get_event_loop()
#     result = await loop.run_in_executor(_executor, lambda: _list_parse_html_using_bs(html_list))

#     return result


# def yt_metadata_scrapper(video_urls: list, timeout: int = 60):
#     """Retrieving a dict of metadata from YT URL input using asyncronous method
#     input:
#         channel_url (list of str) -- an list of url links of input video to be retrieved of its metadata
#         timeout (int, optional) -- a timeout variable for waiting response
#     output: output_dict (dict) -- a dict of metadata, which can be found on function "async_yt_metadata_scrapper"
#     """

#     output = run_async(_yt_metadata_scrapper, video_urls, timeout)

#     output_dict = {"data": output}

#     return output_dict

# %%

# %%
import pandas as pd
from utils.yt_scrapper_utils import *

df = pd.read_pickle("/home/jupyter/cleaned_data_subtitle_yt.pkl")

# %%
df = pd.read_pickle("/home/jupyter/Scraped Video Meta from Channel (ID version).pkl")
# /home/jupyter/Scraped Video Meta from Channel (ID version).pkl
# video_url_list = df.loc[df.index[:3],"video_url"].to_list()
# df_completed = df[~df["video_meta"].isnull()]

# df[["title","duration_s","upload_date"]] = df[["video_meta"]].apply(lambda x: video_meta_retriever(x["video_meta"]), axis=1, result_type="expand")

# df.loc[df["title"].isnull(), "video_meta"] = None
print("All data points: {}".format(df.shape[0]))
# print("Completed Scraping: {}".format(df_completed.shape[0]))

total_downloaded = os.listdir("/home/jupyter/yt_subtitle_data")
print("All downloaded data: {}".format(len(total_downloaded)))

# %%
youtube_prefix_link = "https://www.youtube.com/watch?v="
folder_path_to_save = "/home/jupyter/yt_subtitle_data"
video_urls = list(df["video_url"].unique())
video_id_exists_vtt = set([file[:-7] for file in os.listdir(folder_path_to_save) if file.endswith(".vtt")])
video_id_exists_csv = set([file[:-4] for file in os.listdir(folder_path_to_save) if file.endswith(".csv")])
video_id_exists = video_id_exists_vtt.union(video_id_exists_csv)
video_url_all = set([re.sub(re.escape(youtube_prefix_link),"",url) for url in video_urls])

video_url_to_download = [youtube_prefix_link+id for id in video_url_all.difference(video_id_exists)]

if len(video_url_to_download) <= len(video_url_all):
    print(f"The number of donwloadables is decreasing from {len(video_url_all)} to {len(video_url_to_download)}")

# %%
folder_path_to_save = "/home/jupyter/yt_subtitle_data_test"
ydl_opts = {
            'format': 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4] / wv*+ba/w', #Ensures best settings
            'writesubtitles': True, #Adds a subtitles file if it exists
            'writeautomaticsub': True, #Adds auto-generated subtitles file
            'subtitleslangs' : ["id"], #set the default lang for subtitle (or auto-subtitle)
            'skip_download': True, #skips downloading the video file, if we want to download the vid just change into false
            'outtmpl': os.path.join(folder_path_to_save, '%(id)s.%(ext)s')
        }

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     ydl.download([url])
