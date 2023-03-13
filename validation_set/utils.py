import re
import numbers
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


def lowercase_remove_multiple_space_transform_text(text: str):
    return re.sub("\s+", " ", text.lower())


def remove_non_words_char_transform_text(text: str):
    return re.sub("(?i)[^A-Z0-9\s]+", "", lowercase_remove_multiple_space_transform_text(text))


def parse_sep_token(text: str, list_of_punct: list, sen_token_identifier: str=" [sep] ", word_token_identifier: str=" [word] "):
    re_pat = "\s*" + "(" + "|".join([re.escape(punct) for punct in list_of_punct]) + ")" +"\s*"
    sen_identifier = " " + sen_token_identifier.strip() + " "
    subbed_sen_token = re.sub(re_pat, sen_identifier, lowercase_remove_multiple_space_transform_text(text)).strip()
    return " ".join([word_token_identifier.strip() if word != sen_identifier.strip() else sen_identifier.strip() for word in subbed_sen_token.split(" ")])


def pad_or_truncate_asr_token_seq(token_seq_pred: list or str, actual_seq_len: int, split_on: str=" ", sen_token_identifier: str="sep", word_token_identifier: str="word"):
    for _var, _var_type, _arg_name in zip((token_seq_pred, actual_seq_len, split_on), ((list, str), numbers.Integral, str), ("token_seq_pred", "actual_seq_len", "split_on")):
        if (not isinstance(_var,_var_type)):
            raise TypeError(f"Arg passed type is unexpected for var '{_arg_name}'! Expected {_var_type.__name__}, received {type(_var).__name__}!")

    if isinstance(token_seq_pred, str):
        token_seq_pred = token_seq_pred.split(" ")

    #pad by "[word]" token when it's still not the end, and with "[sep]" at the end
    #trunc until len-1, and pad with "[sep]" at the end
    if len(token_seq_pred) < actual_seq_len:
        num_to_pad = actual_seq_len-len(token_seq_pred)-1
        token_seq_pred.extend([word_token_identifier]*num_to_pad)
        token_seq_pred.append(sen_token_identifier)
    elif len(token_seq_pred) > actual_seq_len:
        idx_to_trunc = actual_seq_len-1
        token_seq_pred = token_seq_pred[:idx_to_trunc]
        token_seq_pred.append(sen_token_identifier)

    return " ".join(token_seq_pred)
