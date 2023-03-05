# %%
import numpy as np
import pandas as pd
from functools import partial
from utils import *

# %%
df = pd.read_csv("result_to_check.csv")
df_other = pd.read_csv("result_to_check_backup.csv")
# %%
df_subtitle = pd.read_feather("/home/jupyter/cleaned_data_subtitle_yt.f")
df_channel_info = pd.read_pickle("/home/jupyter/Scraped Video Meta from Channel (ID Version).pkl")

# %%
col_to_join = ["channel_url", "video_url", "duration_s", "video_meta"]
df_join = df_subtitle.merge(df_channel_info[col_to_join], how="left", left_on="yt_link", right_on="video_url")

# %%
ftr_names = ("len_sen", "unique_word_cnt")
score_weightage = [0.3, 0.7]

df_ftr = pd.DataFrame(dict(zip(("len_sen", "unique_word_cnt"), np.vectorize(get_subtitle_features)(df_join["sen_list"].to_list()))))

df_join = df_join.reset_index(drop=True).merge(df_ftr, left_index=True, right_index=True)

# %%
df_join["scorer"] = np.average([df_join["len_sen"], df_join["unique_word_cnt"]], axis=0, weights=score_weightage)

# %%
quantile_partition = 10
qnt_partial = partial(quantile_fn, quantiles=quantile_partition)
df_qnt_agg_lower = df_join.groupby('channel_url').agg({
    "scorer": partial(qnt_partial, qnt_to_take = 8), "duration_s": partial(qnt_partial, qnt_to_take = 5)}).reset_index().rename(columns={"scorer": "score_thr_low", "duration_s": "duration_s_thr_low"})

df_qnt_agg_higher = df_join.groupby('channel_url').agg({
    "scorer": partial(qnt_partial, qnt_to_take = 9), "duration_s": partial(qnt_partial, qnt_to_take = 8)}).reset_index().rename(columns={"scorer": "score_thr_hi", "duration_s": "duration_s_thr_hi"})

df_join = df_join.merge(df_qnt_agg_lower, how="inner", on="channel_url").merge(df_qnt_agg_higher, how="inner", on="channel_url")

df_to_sample = df_join[(df_join["scorer"].between(df_join["score_thr_low"],df_join["score_thr_hi"])) & (df_join["duration_s"].between(df_join["duration_s_thr_low"],df_join["duration_s_thr_hi"]))]

# %%
top_k = 5
df_val = df_to_sample.groupby('channel_url', group_keys=False).apply(lambda x: x.nlargest(top_k, ["scorer"])).reset_index(drop=True)

# %% from here, the labeler pick 1 video from each channel to be labeled (due to resource limitation for labeler)
df_val.to_csv("result_to_check.csv")
