import re
import numpy as np

def get_subtitle_features(sen_list: list):
    if sen_list is None:
        return 0, 0

    len_sen = len(sen_list)
    words = (" ".join(sen_list)).split(" ")

    unique_word_cnt = len(set(words))

    return len_sen, unique_word_cnt


def scorer(ftr_list:list, scorer:list):
    return np.average(ftr_list, weights=scorer)


def quantile_fn(x, quantiles:int, qnt_to_take:int):
    return np.quantile(x, np.linspace(0, 1, quantiles+1))[qnt_to_take]


def extract_unique_non_words_char(text: str):
    return set(re.findall("(?i)[^A-Z0-9\s]", text))


def text_to_word_sen_token(text: str):
    pass

# def text_cleanser(text:str, remove_all_words_within_parentheses:bool=True):
#     #step 1: remove ascii and strip it
#     text_cleansed = text.encode('ascii', errors='ignore').decode()
#     # print(f"Step 1 Cleanse result: {text_cleansed}")

#     #step 2: remove double whitespace chars (and tail/head spaces)
#     text_cleansed = re.sub("\s{2,}", " ", text_cleansed).strip()
#     # print(f"Step 2 Cleanse result: {text_cleansed}")

#     #step 3: remove any text within parentheses (if toggle is active)
#     if remove_all_words_within_parentheses:
#         # print("Entering remove parentheses")
#         parentheses_set = [("(", ")"), ("{", "}"), ("[", "]")]
#         # print("Check first logic: {}".format(any([re.search(f"\{open_chr}[\w\s]*\{close_chr}", text_cleansed) for open_chr, close_chr in parentheses_set])))
#         while any([re.search(f"\{open_chr}[^\{close_chr}]*\{close_chr}", text_cleansed) for open_chr, close_chr in parentheses_set]):
#             for open_chr, close_chr in parentheses_set:
#                 if re.search(f"\{open_chr}[^\{close_chr}]*\{close_chr}", text_cleansed):
#                     # print(f"Processing to cleanse text with parentheses pair found: {open_chr} {close_chr}")
#                     # print(f"Text input: {text_cleansed}")
#                     text_cleansed = re.sub(f"\s*\{open_chr}[^\{close_chr}]*\{close_chr}\s*", "", text_cleansed)
#                     # print(f"Text cleansed: {text_cleansed}")
        
#         #clease any parentheses remained
#         text_cleansed = re.sub("|".join([re.escape(char) for pairs in parentheses_set for char in pairs]), "", text_cleansed)

#     # print(f"Step 3 Cleanse result: {text_cleansed}")

#     return text_cleansed
