# %% Package Import

import os
from pathlib import Path
from tracemalloc import stop
import pandas as pd
import pickle as pkl
from ast import literal_eval
from datetime import datetime
import re

print("The version of pickle used is {}.".format(pkl.format_version))

# %% Scrape Links

from yt_scraper import channel_video_link_scraper

channel_link = ["https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos",
                "https://www.youtube.com/abc/videos",
                "https://www.youtube.com/c/SharkTankAustralia/videos",
                "https://www.youtube.com/c/DragonsDenGlobal/videos",
                "https://www.youtube.com/c/DragonsDenCanada/videos"]

links_data = channel_video_link_scraper(channel_link)

# %%
all_public_links = []
channel_url = []
for data in links_data["data"]:
    all_public_links.extend(data["public_video_list"])
    channel_url.extend([data["channel_url"]]*len(data["public_video_list"]))

# %%

load_checkpoint_file = True

filename = "Scraped Video Links from Channel.pkl"
save_path = os.path.join(str(Path(os.getcwd()).parents[0]),filename)

if load_checkpoint_file:
    output = pd.read_pickle(save_path)
else: #else, save existing file
    output = pd.DataFrame({"channel_url": channel_url, "video_url": all_public_links})
    output.to_csv(save_path, index=False)
    with open(save_path, "wb") as f:
        pkl.dump(output,f)
    output = pd.DataFrame({"channel_url": channel_url, "video_url": all_public_links})
    
if "video_meta" not in output.columns:
    data_to_scrape = output
else:
    data_to_scrape = output[output.video_meta.isnull()]

data_to_scrape_index = data_to_scrape.index
all_public_links = data_to_scrape.video_url.to_list()
print("First 5 index to be scraped: {}".format(data_to_scrape_index[:5]))
    
# %%

from yt_scraper import yt_metadata_scraper

chunk_number = 10

chunks = [all_public_links[x:x+chunk_number] for x in range(0, len(all_public_links), chunk_number)]

#making batch processing, if it's not completed yet, pls run the previous block
for idx, data in enumerate(chunks):
    print("Processing data of chunk no {} out of {} chunks.".format(idx+1, len(chunks)))
    video_meta = yt_metadata_scraper(data)
    starting_idx = chunk_number*idx
    finishing_idx = min(chunk_number*(idx+1),len(data_to_scrape_index))
    output.loc[data_to_scrape_index[starting_idx:finishing_idx],"video_meta"] = video_meta["data"]
    with open(save_path, "wb") as f:
        pkl.dump(output,f)

print("Finished Scraping YT Metadata!")

# %% extract the meta

def video_meta_retriever(value_to_retrieve: dict):
    """Cast A Misparsed Object from String to its Original Object
    input: value_to_retrieve (str) -- value to be converted
    output: retrieved_value (object from ast_literal result, or None if ValueError) -- returned value
    """
    try:
        retrieved_value = (value_to_retrieve["meta"]["title"],
                        value_to_retrieve["meta"]["duration_s"],
                        value_to_retrieve["meta"]["upload_date"])
    except TypeError as e:
        print(e)
        retrieved_value = (None, None, None)
    return retrieved_value

#change video_meta from string to dict
for index,data in output.iterrows():
    output.loc[index,["title","duration_s","upload_date"]] = video_meta_retriever(data["video_meta"])

output.loc[output["title"].isnull(),"video_meta"] = None

# %% filter data to be downloaded its subtitle

channel_whitelist = ["https://www.youtube.com/channel/UCREgA-BmOocJ9Is_bZV6aJQ/videos",
                     "https://www.youtube.com/c/SharkTankAustralia/videos",
                     "https://www.youtube.com/c/DragonsDenGlobal/videos",
                     "https://www.youtube.com/c/DragonsDenCanada/videos"]

#lower-case and no space
video_title_keyword = ["sharktank", "dragonsden", "dragonden"]

output = output[output["channel_url"].isin(channel_whitelist)|
                output["title"].str.strip().str.lower().str.replace("\W","",regex=True).str.contains("|".join(video_title_keyword))]

print(output.shape)

# %% load checkpoint

load_checkpoint_file = True
filename = "Scraped Video Links from Channel.pkl"
save_path = os.path.join(str(Path(os.getcwd()).parents[0]),filename)


if load_checkpoint_file:
    output = pd.read_pickle(save_path)
else:
    with open(save_path, "wb") as f:
        pkl.dump(output,f)

print(output.info())

# %%
scrape = False

from yt_scraper import yt_subtitle_downloader
from yt_scraper import yt_subtitle_file_vtt_to_csv_converter

download_folder_path = os.path.join(str(Path(os.getcwd()).parents[0]),"yt_subtitle_data")

if scrape:
    
    yt_subtitle_downloader(all_public_links,download_folder_path)
    
    yt_subtitle_file_vtt_to_csv_converter(download_folder_path)

# %%
def neat_csv(csv_folder_path: str=os.getcwd()):
  #Get rid of the white space from the tile
  csv_files = [os.fsdecode(file) for file in os.listdir(csv_folder_path) if os.fsdecode(file).endswith('.csv')]
  
  if len(csv_files) == 0:
      raise ValueError("The length of available csv files under directory {} is 0.".format(csv_folder_path))

#   #Extract the text and videoid
#   vidText = []
#   csv_vidid = []

  for file in enumerate(csv_files):
    df = pd.read_csv(os.path.join(csv_folder_path,file))
#     text = " ".join(df.text) #join the text, so it'll be a whole subtitle text
#     #text = df.text.to_list()
#     vidText.append(text)
#     csv_vidid.append(file[-18:-7])

#   vid_df = pd.DataFrame()
#   vid_df['vid_title'] = clean_csv
#   vid_df['vid_text'] = vidText
#   vid_df['vid_id'] = csv_vidid

#   #Create list of text based on a whole subtitle of each video
#   txt = []
#   splitter = NNSplit.load("en")
#   #t2d = text2digits.Text2Digits()

#   for text in vid_df['vid_text']:
#     splits = splitter.split([text])[0] #Split the text with NLP, to correspond with a sentence

#     a = list([text2int(re.sub(r'(\d)\s+(\d)', r'\1\2', str(sentence))) for sentence in splits])
#     txt.append(a)

#   del vid_df['vid_text']
#   vid_df['text'] = txt

  return df
# %%
foldername = "yt_subtitle_data"
load_path = os.path.join(str(Path(os.getcwd()).parents[0]),foldername)
print(load_path)

output = neat_csv(load_path)
# %%
from nnsplit import NNSplit
splitter = NNSplit.load("en")

text="""
artificial neural networks (ANNs), usually simply called neural networks (NNs), are computing systems inspired by the biological neural networks that constitute animal brains
an ANN is based on a collection of connected units or nodes called artificial neurons, which loosely model the neurons in a biological brain
each connection, like the synapses in a biological brain, can transmit a signal to other neurons
an artificial neuron receives a signal then processes it and can signal neurons connected to it
the "signal" at a connection is a real number, and the output of each neuron is computed by some non-linear function of the sum of its inputs
"""

splits = splitter.split([text])[0] #Split the text with NLP, to correspond with a sentence
# %%
for split in splits:
    print(split)
# %%

start_time_list, stop_time_list = [], []
for index, data in output.iterrows():
    start_time_word, stop_time_word = [], []
    text_to_check = re.sub(data["text"],"\s{2-}"," ")
    start_time = datetime.strptime(data["start"], "%H:%M:%S.f")
    stop_time = datetime.strptime(data["stop"], "%H:%M:%S.f")

    start_time_s = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond/1000
    stop_time_s = stop_time.hour * 3600 + stop_time.minute * 60 + stop_time.second + stop_time.microsecond/1000
    
    # for word in text_to_check.split():

# %%

#make a pair between 2 consecutive rows
#if the len is 1, keep appending, else split the text
#set the start and stop timestamp accordingly
#assumption: a text in a row doesn't consist of 2 sentences

text_appended_list, stop_time_list = [], []
start_time_list = [output.loc[output.index[0],"start"]]

appended_text = output.loc[output.index[0],"text"]
start_time = output.loc[output.index[0],"start"]
stop_time = output.loc[output.index[0],"stop"]

for index, data in output.iterrows():
    if index == output.shape[0]-1:
        text_appended_list.append(appended_text)
        stop_time_list.append(data["stop"])
        break
    
    if appended_text == "":
        appended_text = output.loc[index,"text"]

    print(appended_text)

    if len(splitter.split([appended_text])[0]) > 1:
        print(len(splitter.split([appended_text])[0]))
        text_appended_list.append(appended_text)
        stop_time_list.append(output.loc[index,"stop"])
        appended_text = ""

        start_time_list.append(output.loc[index+1,"start"])
    else:
        appended_text = (appended_text + " " + output.loc[index+1,"text"]).replace("\n", " ")

        
# %%
for index, text in enumerate(text_appended_list, start=1):
    print(index)
    print(text)
# %%
