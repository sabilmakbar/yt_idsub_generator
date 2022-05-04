import os
from pathlib import Path

## new section -- links scrapper

channel_links = [
    # "https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos",
    # "https://www.youtube.com/abc/videos",
    # "https://www.youtube.com/c/SharkTankAustralia/videos",
    # "https://www.youtube.com/c/DragonsDenGlobal/videos",
    "https://www.youtube.com/c/DragonsDenCanada/videos"
]

is_finished = True
foldername_res_video_urls_scrapper = str(Path(os.getcwd()).parents[0])
filename_res_video_urls_scrapper = "Scraped Video Links from Channel_test.pkl"

save_path_res_video_urls_scrapper = os.path.join(foldername_res_video_urls_scrapper, 
                                                 filename_res_video_urls_scrapper)

link_scrapper_params = {
    "channel_url_list": channel_links,
    "checkpoint_bool": is_finished,
    "save_load_path": save_path_res_video_urls_scrapper 
}
