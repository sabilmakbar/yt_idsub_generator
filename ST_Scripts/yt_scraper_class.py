from utils import *

class YTDataScrapper():
    def __init__(self):
        pass

    # A Python Selenium Scraper for Retrieve the List of Links from A Channel
    def channel_video_link_scraper(channel_urls: list):
        return channel_video_link_scraper(channel_urls)

    # A Python BS4 Scraper Collection for Retrieve the Meta Information (Title, Duration)
    def yt_metadata_scraper(video_urls: list, timeout: int = 60):
        return yt_metadata_scraper(video_urls, timeout)

    # A Python Function to extract its auto-subtitle and save it into .vtt format (then converted into .csv)
    def yt_subtitle_downloader(video_urls: list, folder_path_to_save: str = os.getcwd(), ydl_opts : dict=None):
        yt_subtitle_downloader(video_urls, folder_path_to_save, ydl_opts)
        yt_subtitle_file_vtt_to_csv_converter(folder_path_to_save)

