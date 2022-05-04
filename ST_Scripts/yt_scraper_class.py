try:
    from utils.yt_scrapper_utils import *
    from utils.general_utils import *
except ImportError:
    from .utils.yt_scrapper_utils import *
    from .utils.general_utils import *

class YTDataScrapper():
    def __init__(self):
        pass

    # A Python Selenium Scraper for Retrieve the List of Links from A Channel
    def channel_video_link_scrapper(self, channel_urls: list):
        links_data = channel_video_link_scrapper(channel_urls)

        all_public_links = []
        channel_url = []
        for data in links_data["data"]:
            all_public_links.extend(data["public_video_list"])
            channel_url.extend([data["channel_url"]]*len(data["public_video_list"]))

        return channel_url, all_public_links

    # A Python BS4 Scraper Collection for Retrieve the Meta Information (Title, Duration)
    def yt_metadata_scrapper(self, video_urls: list, timeout: int = 60):
        return yt_metadata_scrapper(video_urls, timeout)

    # A Python Function to extract its auto-subtitle and save it into .vtt format (then converted into .csv)
    def yt_subtitle_downloader(self, video_urls: list, folder_path_to_save: str = os.getcwd(), ydl_opts : dict=None):
        yt_subtitle_downloader(video_urls, folder_path_to_save, ydl_opts)
        yt_subtitle_file_vtt_to_csv_converter(folder_path_to_save)


class YTScrapperDF(YTDataScrapper):
    def __init__(self):
        super().__init__()

    # Pandas Output Version of Links Scrapper
    def df_channel_video_link_scrapper(self, video_urls: list):
        channel_url, all_public_links = self.channel_video_link_scrapper(video_urls)
        return iter_to_df_creator(("channel_url", "video_url"), channel_url, all_public_links)

    # Pandas Input Version of Metadata Scrapper (with batch-processing and saving)
    def pd_yt_metadata_scrapper(self, df_input: pd.DataFrame, col_name_meta: str, save_path: str, batch_size: int = 10):
        data_to_scrape = df_input if col_name_meta not in df_input.columns else df_input[df_input[col_name_meta].isnull()]
        data_to_scrape_index = data_to_scrape.index
        all_public_links = data_to_scrape.video_url.to_list()

        print("First 5 index to be scraped: {}".format(data_to_scrape_index[:5]))

        chunks = [all_public_links[x:x+batch_size] for x in range(0, len(all_public_links), batch_size)]

        for idx, data in enumerate(chunks):
            print("Processing data of chunk no {} out of {} chunks.".format(idx+1, len(chunks)))
            video_meta = self.yt_metadata_scrapper(data)
            starting_idx = batch_size*idx
            finishing_idx = min(batch_size*(idx+1),len(data_to_scrape_index))
            df_input.loc[data_to_scrape_index[starting_idx:finishing_idx], col_name_meta] = video_meta["data"]
            df_pickler(save_path, "dump", df_input)
        
        print("Finished Scraping YT Metadata!")

        df_input[["title","duration_s","upload_date"]] = df_input[[col_name_meta]].apply(lambda x: 
                                                        video_meta_retriever(x[col_name_meta]), axis=1, result_type="expand")
        
        df_input.loc[df_input["title"].isnull(), col_name_meta] = None

        print("Finished Unpacking YT Metadata!")
        return df_input

    def video_result_filterer(self, df_input: pd.DataFrame, channel_col_name:str, title_col_name:str, 
                                whitelisted_channels=None, whitelisted_title=None, filter_conditional_and:bool=False):
        
        df_1 = df_filterer(df_input, channel_col_name, None, whitelisted_channels)

        if whitelisted_title is not None:
            try: 
                iter(whitelisted_title) 
            except TypeError as e: 
                pass
            else:
                whitelisted_title = "|".join(whitelisted_title)
        
        df_2 = df_filterer(df_input, title_col_name, "alphanum", whitelisted_title, alpha_lower=True)

        if filter_conditional_and:
            df_filtered_index = df_1.index.intersection(df_2.index)
        else:
            df_filtered_index = df_1.index.union(df_2.index)
        
        df_input = df_input.loc[df_filtered_index, :]

        return df_input
