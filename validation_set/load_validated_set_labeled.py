# %%
import re
import numpy as np
import pandas as pd

import os

#chdir to its parent
os.chdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import sys
print(sys.path)
# %% CONFIGS
sen_sep_token = " [sep] "
sen_token_identifier = "sep"
word_token_identifier = "word"

# %%
df_val = pd.read_csv("validation_set/validated_video_subtitles_cleaned.csv")
df_subtitle_cleaned = pd.read_feather("result_file_example/cleaned_data_langdetect_subtitle_yt_post_processed.f")

# %%
df_val.rename(columns={"subtitles": "subtitle_ground_truth"}, inplace=True)
df_subtitle_cleaned = df_subtitle_cleaned[["vid_id", "subtitle_cleaned"]]

df_join = df_val.merge(df_subtitle_cleaned, how="inner", left_on="video_id", right_on="vid_id")
df_join.drop(columns="vid_id", inplace=True)
df_join["subtitle_asr"] = df_join["subtitle_cleaned"].str.replace(re.escape(sen_sep_token), ". ", regex=True)

# %%
import jiwer
import jiwer.transforms as tr
from functools import partial
from utils import remove_non_words_char_transform_text

wer_tr_settings = tr.Compose([tr.RemoveMultipleSpaces(), tr.ToLowerCase(), tr.ReduceToListOfListOfWords()])
wer_no_tr_settings = tr.Compose([tr.ReduceToListOfListOfWords()])
cer_tr_settings = tr.Compose([tr.RemoveMultipleSpaces(), tr.ToLowerCase(), tr.ReduceToListOfListOfChars()])
cer_no_tr_settings = tr.Compose([tr.ReduceToListOfListOfChars()])

wer_transform = partial(jiwer.wer, truth_transform=wer_tr_settings, hypothesis_transform=wer_tr_settings)
wer_no_transform = partial(jiwer.wer, truth_transform=wer_no_tr_settings, hypothesis_transform=wer_no_tr_settings)
cer_transform = partial(jiwer.cer, truth_transform=cer_tr_settings, hypothesis_transform=cer_tr_settings)
cer_no_transform = partial(jiwer.cer, truth_transform=cer_no_tr_settings, hypothesis_transform=cer_no_tr_settings)

df_join["wer_score_tr"] = np.vectorize(wer_transform)(df_join["subtitle_ground_truth"], df_join["subtitle_asr"])
df_join["wer_score_no_tr"] = np.vectorize(wer_no_transform)(df_join["subtitle_ground_truth"], df_join["subtitle_asr"])
df_join["wer_score_no_punct_tr"] = np.vectorize(wer_no_transform)(df_join["subtitle_ground_truth"].apply(remove_non_words_char_transform_text), df_join["subtitle_asr"].apply(remove_non_words_char_transform_text))

df_join["cer_score_tr"] = np.vectorize(cer_no_transform)(df_join["subtitle_ground_truth"], df_join["subtitle_asr"])
df_join["cer_score_no_tr"] = np.vectorize(cer_no_transform)(df_join["subtitle_ground_truth"], df_join["subtitle_asr"])
df_join["cer_score_no_punct_tr"] = np.vectorize(cer_no_transform)(df_join["subtitle_ground_truth"].apply(remove_non_words_char_transform_text), df_join["subtitle_asr"].apply(remove_non_words_char_transform_text))

# %%
print(f'Average WER (w/ Punctuation): {df_join["wer_score_tr"].mean()}')
print(f'Average CER (w/ Punctuation): {df_join["cer_score_tr"].mean()}')

print(f'Average WER (w/o Punctuation): {df_join["wer_score_no_punct_tr"].mean()}')
print(f'Average CER (w/o Punctuation): {df_join["cer_score_no_punct_tr"].mean()}')

# %% check what's the non-word chars on both
from utils import extract_unique_non_words_char
set_asr = set().union(*list(map(extract_unique_non_words_char, df_join["subtitle_asr"])))
set_gt = set().union(*list(map(extract_unique_non_words_char, df_join["subtitle_ground_truth"])))

# %% define char to be changed into sep
set_asr = {"."}
set_gt = {".", "?"}

# %% find the error rate of punctuation tokens
from utils import parse_sep_token

partial_parse_sep_token_gt = lambda x: parse_sep_token(x, list(set_gt), sen_token_identifier, word_token_identifier)

df_join["subtitle_gt_tokenized"] = np.vectorize(partial_parse_sep_token_gt)(df_join["subtitle_ground_truth"])
df_join["subtitle_asr_tokenized"] = np.vectorize(partial_parse_sep_token_gt)(df_join["subtitle_asr"])

df_join["sep_error_rate_wer"] = np.vectorize(wer_no_transform)(df_join["subtitle_gt_tokenized"], df_join["subtitle_asr_tokenized"])

# %% find the error rate of punctuation tokens using seqeval (by padding/truncating)
from utils import pad_or_truncate_asr_token_seq
from seqeval.metrics import classification_report

df_join["len_subtitle_gt_tokenized"] = df_join["subtitle_gt_tokenized"].apply(lambda x: len(x.split(" ")))
df_join["len_subtitle_asr_tokenized"] = df_join["subtitle_asr_tokenized"].apply(lambda x: len(x.split(" ")))

df_join["subtitle_asr_tokenized_adj"] = np.vectorize(pad_or_truncate_asr_token_seq)(df_join["subtitle_asr_tokenized"], df_join["len_subtitle_gt_tokenized"])
y_true_list = list(df_join["subtitle_gt_tokenized"].str.split(" "))
y_pred_list = list(df_join["subtitle_asr_tokenized_adj"].str.split(" "))

seqeval_res = classification_report(y_true=y_true_list, y_pred=y_pred_list)
print(seqeval_res)

# %%
