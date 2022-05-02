import os
from pathlib import Path


## new section -- links scrapper

channel_links = [
    "https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos",
    "https://www.youtube.com/abc/videos",
    "https://www.youtube.com/c/SharkTankAustralia/videos",
    "https://www.youtube.com/c/DragonsDenGlobal/videos",
    "https://www.youtube.com/c/DragonsDenCanada/videos"
]

checkpoint_video_urls_scrapper = True
foldname_res_video_urls_scrapper = str(Path(os.getcwd()).parents[0])
filename_res_video_urls_scrapper = "Scraped Video Links from Channel.pkl"

save_path_res_video_urls_scrapper = os.path.join(foldname_res_video_urls_scrapper, 
                                                 filename_res_video_urls_scrapper)

link_scrapper_params = {
    "channel_url_list": channel_links,
    "checkpoint_bool": checkpoint_video_urls_scrapper,
    "save_load_path": save_path_res_video_urls_scrapper 
}

## new section -- meta scrapper
num_batch_meta_scrapper = 10
whitelisted_channels_scrapped = [
    "https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos",
    "https://www.youtube.com/c/SharkTankAustralia/videos",
    "https://www.youtube.com/c/DragonsDenGlobal/videos",
    "https://www.youtube.com/c/DragonsDenCanada/videos"
]

#lowercase no sym
whitelisted_title_phrases = [
    "sharktank", "dragonsden", "dragonden"
]

#save it as pickle
checkpoint_video_meta_scrapper = True
foldname_res_video_meta_scrapper = str(Path(os.getcwd()).parents[0])
filename_res_video_meta_scrapper = "Scraped Video Meta from Channel.pkl"

save_path_res_video_meta_scrapper = os.path.join(foldname_res_video_urls_scrapper, 
                                                 filename_res_video_urls_scrapper)

meta_scrapper_params = {
    "n_batch": num_batch_meta_scrapper,
    "whitelisted_channels": whitelisted_channels_scrapped,
    "whitelisted_titles_phrase": whitelisted_title_phrases,
    "checkpoint_bool": checkpoint_video_meta_scrapper,
    "save_load_path": save_path_res_video_meta_scrapper
}

## new section -- subtitle scrapper