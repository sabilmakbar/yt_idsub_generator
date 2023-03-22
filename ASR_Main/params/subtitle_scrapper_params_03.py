import os
from pathlib import Path

## new section -- links scrapper

is_finished_downloading = True
is_finished_processing = True

# foldername_res_video_urls_scrapper = str(Path(os.getcwd()).parents[0])
foldername_res_video_urls_scrapper = os.getcwd()
child_folder_name = "yt_subtitle_data"

df_links_col_name = "video_url"

yt_dlp_options = None

save_path_res_video_urls_scrapper = os.path.join(foldername_res_video_urls_scrapper, 
                                                 child_folder_name)

final_csv_pickle_name = "cleaned_data_subtitle_yt.pkl"

subtitle_scrapper_params = {
    "checkpoint_bool_downloading": is_finished_downloading,
    "save_load_path": save_path_res_video_urls_scrapper,
    "df_links_col_name": df_links_col_name,
    "yt_dlp_options": yt_dlp_options,

    "checkpoint_bool_processing": is_finished_processing,
    "save_final_path": os.path.join(foldername_res_video_urls_scrapper, final_csv_pickle_name)
}
