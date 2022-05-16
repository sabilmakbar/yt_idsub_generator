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
save_path_links = link_scrapper_params["save_load_path"]

output = scrapper_df.df_loader_or_dumper(save_path_links, load_checkpoint_file, scrapper_df.df_channel_video_link_scrapper, video_urls = link_scrapper_params["channel_url_list"])

# %%

output = scrapper_df.pd_yt_metadata_scrapper(output, "video_meta", save_path_links, meta_scrapper_params["batch_size"])

# %% filter data to be downloaded its subtitle

channel_whitelist = meta_scrapper_params["whitelisted_channels"]

video_title_keyword = meta_scrapper_params["whitelisted_titles_phrase"]

load_checkpoint_file = meta_scrapper_params["checkpoint_bool"]
save_path = meta_scrapper_params["save_load_path"]

output = scrapper_df.df_loader_or_dumper(save_path_links, load_checkpoint_file, scrapper_df.video_result_filterer, df_input=output, 
                                         channel_col_name="channel_url", title_col_name="title", whitelisted_channels=channel_whitelist, whitelisted_title=video_title_keyword)

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
# #   vid_df['vid_title'] = csv_files_name
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
