# %%
import re
import numpy as np
import pandas as pd

df_val = pd.read_csv("validated_video_subtitles_cleaned.csv")
df_subtitle_cleaned = pd.read_feather()

# %%
df_subtitle_cleaned = df_subtitle_cleaned[["vid_id", "channel_url", "sen_list"]]

df_join = df_val.merge(df_subtitle_cleaned, how="inner", left_on="video_id", right_on="vid_id")
df_join.drop(columns="vid_id", inplace=True)

# %%
