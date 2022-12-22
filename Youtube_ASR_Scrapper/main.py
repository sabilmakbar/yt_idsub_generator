# %% Package Import
import os
from pathlib import Path
import pandas as pd
import pickle as pkl
from datetime import datetime

try:
    from yt_scraper_class import YTScrapperDF, YTDataScrapper as YTGeneralScrapper
    from splitter_class import TextSplitter
    from utils.general_utils import *
    from params.link_scrapper_params_01 import link_scrapper_params
    from params.meta_scrapper_params_02 import meta_scrapper_params
    from params.subtitle_scrapper_params_03 import subtitle_scrapper_params

except ImportError: #do a relative import
    from .yt_scraper_class import YTScrapperDF, YTDataScrapper as YTGeneralScrapper
    from .splitter_class import TextSplitter
    from .utils.general_utils import *
    from .params.link_scrapper_params_01 import link_scrapper_params
    from .params.meta_scrapper_params_02 import meta_scrapper_params
    from .params.subtitle_scrapper_params_03 import subtitle_scrapper_params

scrapper_df = YTScrapperDF()
scrapper_general = YTGeneralScrapper()
splitter_class_nn = TextSplitter(lang="en")

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
do_scrape = not(subtitle_scrapper_params["checkpoint_bool_downloading"])

download_lists = output[subtitle_scrapper_params["df_links_col_name"]].drop_duplicates().to_list()
download_folder_path = subtitle_scrapper_params["save_load_path"]

yt_dlp_options = subtitle_scrapper_params["yt_dlp_options"]

if do_scrape:
    scrapper_general.yt_subtitle_downloader(download_lists, download_folder_path, yt_dlp_options)
    if len(os.listdir(download_folder_path) != len(download_lists)):
        raise AssertionError("The length of the downloaded subtitle doesn't match with its expected!")

# %%
do_data_process = not(subtitle_scrapper_params["checkpoint_bool_processing"])

save_final_path = subtitle_scrapper_params["save_final_path"]

output = scrapper_df.df_loader_or_dumper(save_final_path, do_data_process, scrapper_df.split_yt_subtitles, splitter=splitter_class_nn, df_path=download_folder_path)
