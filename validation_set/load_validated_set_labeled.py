# %%
import re
import numpy as np
import pandas as pd

df_sampled = pd.read_csv("result_to_check.csv")
df_val = pd.read_csv("validated_video_subtitles.csv")

# %%
df_sampled_subset = df_sampled[["vid_id", "channel_url", "sen_list"]]

df_join = df_val.merge(df_sampled_subset, how="inner", left_on="video_id", right_on="vid_id")
df_join.drop(columns="vid_id", inplace=True)

# %%
non_word_char_regex = "[^\w\s]"
sentence_punctuations_list = [".", ",", "!", "?"]
parentheses_list = ["(", "{", "[", ")", "}", "]"]
set_chars_to_exclude = set(sentence_punctuations_list).union(set(parentheses_list))

df_join["non_word_char"] = df_join["subtitles"].apply(lambda x: list(set(re.findall(non_word_char_regex, x))))
df_join["non_word_char_excl_punct_and_parentheses"] = df_join["non_word_char"].apply(lambda x: list(set(x).difference(set_chars_to_exclude)))
df_join["re_statement_to_check_words"] = df_join["non_word_char_excl_punct_and_parentheses"].apply(lambda x: "(?:" + "|".join([re.escape(char) for char in x]) + ")")

# %%
num_of_words_to_capture = 5
bracket_pat = "0,{}".format(num_of_words_to_capture)
following_re_pat = "(?:(?:\S*\s*)|(?:\s*\S*)){re_pat}".format(re_pat="{"+bracket_pat+"}")
prev_re_pat = "(?:(?:\S*\s*)|(?:\s*\S*)){re_pat}".format(re_pat="{"+bracket_pat+"}")
df_join["{}_words_surronds_selected_char".format(num_of_words_to_capture)] = df_join.apply(lambda val: re.findall("({}{}{})".format(prev_re_pat, val["re_statement_to_check_words"], following_re_pat), val["subtitles"]) if val["re_statement_to_check_words"] != "" else [], axis=1)

# %%
