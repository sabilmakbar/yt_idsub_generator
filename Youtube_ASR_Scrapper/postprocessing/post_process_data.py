# %%
import os
import re
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import pandas as pd

from functools import partial

from utils import get_text_in_brackets, detect_non_ascii
df = pd.read_feather("result_file_example/cleaned_data_subtitle_yt.f")

# %% concat sentence list in subtitle data that has been scraped
df["subtitle"] = df["sen_list"].apply(lambda x: f" ".join(x) if x is not None else x)

get_text_in_brackets = partial(get_text_in_brackets, return_distinct=True)
df["text_in_bracket"] = df["subtitle"].apply(get_text_in_brackets)
df["non_ascii_text"] = df["subtitle"].apply(detect_non_ascii)

# %% get any non-ascii text see whether it needs to be removed (by eye-test)
to_inspect_non_ascii = (df.loc[(df["non_ascii_text"].apply(len) > 0), "non_ascii_text"]).to_frame().explode("non_ascii_text",ignore_index=True)
to_inspect_non_ascii_set = to_inspect_non_ascii.drop_duplicates()["non_ascii_text"].to_list()

# %% get any text enclosed in parentheses and see whether it needs to be removed (by eye-test)
df_text_in_brackets = pd.DataFrame(df["text_in_bracket"].to_list(), columns=["round", "curly", "squared"], index=df.index)
to_inspect_round = (df_text_in_brackets.loc[(df_text_in_brackets["round"].apply(len) > 0), "round"]).to_frame().explode("round",ignore_index=True)
to_inspect_curly = (df_text_in_brackets.loc[(df_text_in_brackets["curly"].apply(len) > 0), "curly"]).to_frame().explode("curly",ignore_index=True)
to_inspect_squared = (df_text_in_brackets.loc[(df_text_in_brackets["squared"].apply(len) > 0), "squared"]).to_frame().explode("squared",ignore_index=True)

to_inspect_round_set = to_inspect_round.drop_duplicates()["round"].to_list()
to_inspect_curly_set = to_inspect_curly.drop_duplicates()["curly"].to_list()
to_inspect_squared_set = to_inspect_squared.drop_duplicates()["squared"].to_list()

# %% cleanse the subtitle text based on eye-testing result
# eye-test decision on non-ASCII chars: remove all of them
# eye-test decision on brackets: remove all chars enclosed by square brackets (as it contain non-meaningful words)
from utils import delete_text_in_unbalanced_brackets, remove_non_ascii, iterator_text_fn_applier
from config import sen_token, bracket_pair_list_to_cleanse

delete_text_in_unbalanced_squared_brackets = partial(delete_text_in_unbalanced_brackets, bracket_pair_list=bracket_pair_list_to_cleanse)
fn_to_apply = lambda text_list: iterator_text_fn_applier(iter_obj=text_list, fn=lambda x: delete_text_in_unbalanced_squared_brackets(remove_non_ascii(x)), raiseNoneObjEval=False, return_iter=False, concat_token=sen_token)

# %% apply preprocess fn to subtitle list
df["subtitle_cleaned"] = df["sen_list"].apply(fn_to_apply)

# %% get any text enclosed in parentheses again and see whether it has been truly cleansed (aside from sentence separator token)
get_text_in_brackets = partial(get_text_in_brackets, return_distinct=True, bracket_pair_list=bracket_pair_list_to_cleanse)
df["text_in_bracket_squared"] = df["subtitle_cleaned"].apply(get_text_in_brackets)

df_text_in_squared_brackets = pd.DataFrame(df["text_in_bracket_squared"].to_list(), columns=["squared"], index=df.index)
to_inspect_squared_cleanse_ver = (df_text_in_squared_brackets.loc[(df_text_in_squared_brackets["squared"].apply(len) > 0), "squared"]).to_frame().explode("squared",ignore_index=True)
to_inspect_squared_cleanse_ver_set = to_inspect_squared_cleanse_ver.drop_duplicates()["squared"].to_list()

# %%
from utils import get_langdetect_result
from config import langdetect_interest_list

df.dropna(subset=["subtitle_cleaned"], inplace=True)

df.reset_index(drop=True, inplace=True)
df["langdetect_result"] = df["subtitle_cleaned"].apply(lambda x: get_langdetect_result(re.sub(f" {re.escape(sen_token)} ", " ", x), langdetect_interest_list))

langdetect_res = pd.json_normalize(df["langdetect_result"])
df = df.merge(langdetect_res, left_index=True, right_index=True, how="left")

langdetect_res = langdetect_res[(langdetect_res["id"]>=0.95) | ((langdetect_res["id"]>=0.9) & (langdetect_res["en"]>=0.05))]

df_filtered = df.loc[langdetect_res.index, :].reset_index(drop=True)

# %% export cleansed data (with column values readjusted)

df_export_cleaned = df_filtered.drop(columns=["text_in_bracket", "non_ascii_text", "subtitle", "sen_list", "start_list", "stop_list", "text_in_bracket_squared"])
df_export_cleaned.to_feather("result_file_example/cleaned_data_langdetect_subtitle_yt_post_processed.f")

df_export = df.drop(columns=["text_in_bracket", "non_ascii_text", "subtitle", "sen_list", "start_list", "stop_list", "text_in_bracket_squared"])
df_export.to_feather("result_file_example/cleaned_data_subtitle_yt_post_processed.f")

# %%
