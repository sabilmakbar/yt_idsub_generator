# %% Package Import
import os
from pathlib import Path
# %% Scrape Links
from yt_scraper import channel_video_link_scraper

links = channel_video_link_scraper("https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos")

# %%
from yt_scraper import yt_metadata_scraper
#to be tested soon: https://www.thepythoncode.com/article/get-youtube-data-python (using direct BS4)

video_meta = yt_metadata_scraper(links[0])

video_meta

# %%
from yt_scraper import yt_subtitle_downloader

download_folder_path = os.path.join(str(Path(os.getcwd()).parents[0]),"yt_subtitle_data")

yt_subtitle_downloader([links[0]],download_folder_path)
# %%
from yt_scraper import yt_subtitle_file_vtt_to_csv_converter

saved_folder_path = os.path.join(str(Path(os.getcwd()).parents[0]),"yt_subtitle_data")

yt_subtitle_file_vtt_to_csv_converter(download_folder_path)

# %%
