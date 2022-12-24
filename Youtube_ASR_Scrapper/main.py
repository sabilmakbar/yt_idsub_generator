if __name__ == "__main__":

    #Package Import
    import os
    import pickle
    import pandas as pd


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
    print("The version of pickle used is {}.".format(pickle.format_version))
    print("The version of pandas used is {}.".format(pd.__version__))

    #scrape YT links from given channel
    load_checkpoint_file = link_scrapper_params["checkpoint_bool"]
    save_path_links = link_scrapper_params["save_load_path"]

    output_links_from_channel = scrapper_df.df_loader_or_dumper(save_path_links, load_checkpoint_file, scrapper_df.df_channel_video_link_scrapper, video_urls = link_scrapper_params["channel_url_list"])

    #scrape YT metadata from links
    output_meta_from_links = scrapper_df.pd_yt_metadata_scrapper(output_links_from_channel, "video_meta", save_path_links, meta_scrapper_params["batch_size"])

    #filter YT links from blacklist/whitelist params to be downloaded its subtitle later
    channel_whitelist = meta_scrapper_params["whitelisted_channels"]
    video_title_keyword = meta_scrapper_params["whitelisted_titles_phrase"]
    load_checkpoint_file = meta_scrapper_params["checkpoint_bool"]
    save_path_with_meta = meta_scrapper_params["save_load_path"]

    output_meta_from_links_filtered = scrapper_df.df_loader_or_dumper(save_path_with_meta, load_checkpoint_file, scrapper_df.video_result_filterer, df_input=output_meta_from_links,
                                                  channel_col_name="channel_url", title_col_name="title", whitelisted_channels=channel_whitelist, whitelisted_title=video_title_keyword)

    #scrape YT subtitles
    do_scrape = not(subtitle_scrapper_params["checkpoint_bool_downloading"])
    download_lists = output_meta_from_links_filtered[subtitle_scrapper_params["df_links_col_name"]].drop_duplicates().to_list()
    download_folder_path = subtitle_scrapper_params["save_load_path"]

    yt_dlp_options = subtitle_scrapper_params["yt_dlp_options"]

    if do_scrape:
        scrapper_general.yt_subtitle_downloader(download_lists, download_folder_path, yt_dlp_options)
        if len(os.listdir(download_folder_path)) != len(download_lists):
            raise AssertionError("The length of the downloaded subtitle doesn't match with its expected!")

    #process its subtitle data into final dataset
    do_data_process = subtitle_scrapper_params["checkpoint_bool_processing"]
    save_final_path = subtitle_scrapper_params["save_final_path"]

    output = scrapper_df.df_loader_or_dumper(save_final_path, do_data_process, scrapper_df.scrapper_split_yt_subtitles, splitter=splitter_class_nn, df_path=download_folder_path, subtitle_col_name="text", start_stamp_col_name="start", stop_stamp_col_name="stop")
