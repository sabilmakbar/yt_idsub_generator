import os
from pathlib import Path

num_batch_meta_scrapper = 10
whitelisted_channels_scrapped = None

#lowercase no sym
whitelisted_title_phrases = None

#save it as pickle
is_finished = True
# foldername_res_video_meta_scrapper = str(Path(os.getcwd()).parents[0])
foldername_res_video_meta_scrapper = os.getcwd()
filename_res_video_meta_scrapper = "Scraped Video Meta from Channel (ID Version).pkl"

save_path_res_video_meta_scrapper = os.path.join(foldername_res_video_meta_scrapper, 
                                                 filename_res_video_meta_scrapper)

meta_scrapper_params = {
    "batch_size": num_batch_meta_scrapper,
    "whitelisted_channels": whitelisted_channels_scrapped,
    "whitelisted_titles_phrase": whitelisted_title_phrases,
    "checkpoint_bool": is_finished,
    "save_load_path": save_path_res_video_meta_scrapper
}
