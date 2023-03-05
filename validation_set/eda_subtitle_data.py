# %%
import re

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# %%
df_subtitle = pd.read_feather()

non_word_char_regex = "[^\w\s]"
sentence_punctuations_list = [".", ",", "!", "?"]
parentheses_list = ["(", "{", "[", ")", "}", "]"]
set_chars_to_exclude = set(sentence_punctuations_list).union(set(parentheses_list))

df_subtitle["non_word_char"] = df_subtitle["subtitles"].apply(lambda x: list(set(re.findall(non_word_char_regex, x))))
df_subtitle["non_word_char_excl_punct_and_parentheses"] = df_subtitle["non_word_char"].apply(lambda x: list(set(x).difference(set_chars_to_exclude)))
df_subtitle["re_statement_to_check_words"] = df_subtitle["non_word_char_excl_punct_and_parentheses"].apply(lambda x: "(?:" + "|".join([re.escape(char) for char in x]) + ")")

# %%
num_of_words_to_capture = 2
bracket_pat = "0,{}".format(num_of_words_to_capture)
following_re_pat = "(?:(?:\S*\s*)|(?:\s*\S*)){re_pat}".format(re_pat="{"+bracket_pat+"}")
prev_re_pat = "(?:(?:\S*\s*)|(?:\s*\S*)){re_pat}".format(re_pat="{"+bracket_pat+"}")
df_subtitle["{}_words_surronds_selected_char".format(num_of_words_to_capture)] = df_subtitle.apply(lambda val: re.findall("({}{}{})".format(prev_re_pat, val["re_statement_to_check_words"], following_re_pat), val["subtitles"]) if val["re_statement_to_check_words"] != "" else [], axis=1)
