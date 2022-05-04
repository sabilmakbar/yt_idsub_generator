# %% Package Import

import os
from pathlib import Path
import pandas as pd
import pickle as pkl
from datetime import datetime
import re

try:
    from yt_scraper_class import YTScrapperDF, YTDataScrapper as YTGeneralScrapper
    from utils.general_utils import *
    from params.link_scrapper_params import link_scrapper_params
    from params.meta_scrapper_params import meta_scrapper_params
    from params.subtitle_scrapper_params import subtitle_scrapper_params

except ImportError: #do a relative import
    from .yt_scraper_class import YTScrapperDF, YTDataScrapper as YTGeneralScrapper
    from .utils.general_utils import *
    from .params.link_scrapper_params import link_scrapper_params
    from .params.meta_scrapper_params import meta_scrapper_params
    from .params.subtitle_scrapper_params import subtitle_scrapper_params

scrapper_df = YTScrapperDF()
scrapper_general = YTGeneralScrapper()

#pickle versioning is important bcs of different versions could lead to pickling error
print("The version of pickle used is {}.".format(pkl.format_version))

# %% 

load_checkpoint_file = link_scrapper_params["checkpoint_bool"]
save_path = link_scrapper_params["save_load_path"]

actions = "load" if load_checkpoint_file else "dump"
scrapper_result = None if actions=="load" else scrapper_df.df_channel_video_link_scrapper(link_scrapper_params["channel_url_list"])

output = df_pickler(save_path, actions, scrapper_result)

# %%

output = scrapper_df.pd_yt_metadata_scrapper(output, "video_meta", save_path, meta_scrapper_params["batch_size"])

# %% filter data to be downloaded its subtitle

channel_whitelist = meta_scrapper_params["whitelisted_channels"]

video_title_keyword = meta_scrapper_params["whitelisted_titles_phrase"]

output = scrapper_df.video_result_filterer(output, "channel_url", "title", channel_whitelist, video_title_keyword)

print(output.shape)

# %% load checkpoint
load_checkpoint_file = meta_scrapper_params["checkpoint_bool"]
save_path = meta_scrapper_params["save_load_path"]

actions = "load" if load_checkpoint_file else "dump"
scrapper_result = None if actions=="load" else output

output = df_pickler(save_path, actions, scrapper_result)

# %%
do_scrape = not(subtitle_scrapper_params["checkpoint_bool"])

download_lists = output[subtitle_scrapper_params["df_links_col_name"]].drop_duplicates().to_list()
download_folder_path = subtitle_scrapper_params["save_load_path"]

yt_dlp_options = None if subtitle_scrapper_params["yt_dlp_options"] is None else subtitle_scrapper_params["yt_dlp_options"]
    

if do_scrape:
    scrapper_general.yt_subtitle_downloader(download_lists, download_folder_path, yt_dlp_options)

# %%
# def neat_csv(csv_folder_path: str=os.getcwd()):
#   #Get rid of the white space from the tile
#   csv_files = [os.fsdecode(file) for file in os.listdir(csv_folder_path) if os.fsdecode(file).endswith('.csv')]
  
#   if len(csv_files) == 0:
#       raise ValueError("The length of available csv files under directory {} is 0.".format(csv_folder_path))

# #   #Extract the text and videoid
# #   vidText = []
# #   csv_vidid = []

#   for file_name in enumerate(csv_files_name):
#     df = pd.read_csv(os.path.join(csv_folder_path,file_name))
# #     text = " ".join(df.text) #join the text, so it'll be a whole subtitle text
# #     #text = df.text.to_list()
# #     vidText.append(text)
# #     csv_vidid.append(file[-18:-7])

# #   vid_df = pd.DataFrame()
# #   vid_df['vid_title'] = clean_csv
# #   vid_df['vid_text'] = vidText
# #   vid_df['vid_id'] = csv_vidid

# #   #Create list of text based on a whole subtitle of each video
# #   txt = []
# #   splitter = NNSplit.load("en")
# #   #t2d = text2digits.Text2Digits()

# #   for text in vid_df['vid_text']:
# #     splits = splitter.split([text])[0] #Split the text with NLP, to correspond with a sentence

# #     a = list([text2int(re.sub(r'(\d)\s+(\d)', r'\1\2', str(sentence))) for sentence in splits])
# #     txt.append(a)

# #   del vid_df['vid_text']
# #   vid_df['text'] = txt

#   return df
# # %%
# foldername = "yt_subtitle_data"
# load_path = os.path.join(str(Path(os.getcwd()).parents[0]),foldername)
# print(load_path)

# output = neat_csv(load_path)
# %%
# from nnsplit import NNSplit
# splitter = NNSplit.load("en")

# text="""
# artificial neural networks (ANNs), usually simply called neural networks (NNs), are computing systems inspired by the biological neural networks that constitute animal brains
# an ANN is based on a collection of connected units or nodes called artificial neurons, which loosely model the neurons in a biological brain
# each connection, like the synapses in a biological brain, can transmit a signal to other neurons
# an artificial neuron receives a signal then processes it and can signal neurons connected to it
# the "signal" at a connection is a real number, and the output of each neuron is computed by some non-linear function of the sum of its inputs
# """

# splits = splitter.split([text])[0] #Split the text with NLP, to correspond with a sentence
# # %%
# for split in splits:
#     print(split)
# # %%

# start_time_list, stop_time_list = [], []
# for index, data in output.iterrows():
#     start_time_word, stop_time_word = [], []
#     text_to_check = re.sub(data["text"],"\s{2-}"," ")
#     start_time = datetime.strptime(data["start"], "%H:%M:%S.f")
#     stop_time = datetime.strptime(data["stop"], "%H:%M:%S.f")

#     start_time_s = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond/1000
#     stop_time_s = stop_time.hour * 3600 + stop_time.minute * 60 + stop_time.second + stop_time.microsecond/1000
    
#     # for word in text_to_check.split():

