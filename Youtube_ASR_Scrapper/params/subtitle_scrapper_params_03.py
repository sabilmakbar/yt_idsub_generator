import os
from pathlib import Path

## new section -- links scrapper

is_finished = False
foldername_res_video_urls_scrapper = str(Path(os.getcwd()).parents[0])
child_folder_name = "yt_subtitle_data"

df_links_col_name = "video_url"

yt_dlp_options = None

save_path_res_video_urls_scrapper = os.path.join(foldername_res_video_urls_scrapper, 
                                                 child_folder_name)

subtitle_scrapper_params = {
    "checkpoint_bool": is_finished,
    "save_load_path": save_path_res_video_urls_scrapper,
    "df_links_col_name": df_links_col_name,
    "yt_dlp_options": yt_dlp_options
}
