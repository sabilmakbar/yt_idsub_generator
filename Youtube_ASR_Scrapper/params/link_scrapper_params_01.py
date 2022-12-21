import os
from pathlib import Path

channel_links = [
    "https://www.youtube.com/@DaftarPopuler/videos",
    "https://www.youtube.com/@kompastv/videos",
    "https://www.youtube.com/@tvOneNews/videos",
    "https://www.youtube.com/@CNNindonesiaOfficial/videos",
    "https://www.youtube.com/@tribuntimur/videos",
    "https://www.youtube.com/@MetrotvnewsOfficial/videos",
    "https://www.youtube.com/@VideoOnthespotChannel/videos",
    "https://www.youtube.com/@CNBC_ID/videos",
    "https://www.youtube.com/@kumparan/videos",
    "https://www.youtube.com/@detikcom/videos"
]

is_finished = False
foldername_res_video_urls_scrapper = str(Path(os.getcwd()).parents[0])
filename_res_video_urls_scrapper = "Scraped Video Links from Channel (ID Version).pkl"

save_path_res_video_urls_scrapper = os.path.join(foldername_res_video_urls_scrapper, 
                                                 filename_res_video_urls_scrapper)

link_scrapper_params = {
    "channel_url_list": channel_links,
    "checkpoint_bool": is_finished,
    "save_load_path": save_path_res_video_urls_scrapper 
}
