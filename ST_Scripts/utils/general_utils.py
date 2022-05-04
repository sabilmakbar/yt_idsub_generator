import pandas as pd
import re
from datetime import datetime as dt
import pickle

def dt_str_stamp_lin(start, end, text:str, time_format = "%H:%M:%S"):
    text = re.sub(r"\s+", r" ", text)
    word_pos = [(ele.start()+1, ele.end()+1) for ele in re.finditer(r'\S+', text)]
    text_len = len(text)

    word_dt_stamp = list()

    def lin_pos_dt_stamp(str_pos):
        stamp = dt.strptime(start, time_format) + (dt.strptime(end, time_format) - dt.strptime(start, time_format))*(str_pos-1)/text_len
        return dt.strftime(stamp, time_format+r".%f")

    for start_word_pos, end_word_pos in word_pos:
        word_dt_stamp.append((lin_pos_dt_stamp(start_word_pos), lin_pos_dt_stamp(end_word_pos)))

    return word_dt_stamp, word_pos, text

def iter_to_df_creator(*args):
    #first argument for column name, second and later for columns
    col_names = args[0]
    values = args[1:]

    return pd.DataFrame(dict(zip(col_names, values)))

def df_pickler(file_path: str, actions: str, df_input=None):
    if actions not in ["load", "dump"]: raise AssertionError("Actions Incorrect! Must be either 'dump' or 'load'!")

    txt_file_path = file_path[:-4]+".txt"
    if actions == "dump":
        if df_input is None or not isinstance(df_input, pd.DataFrame): raise AssertionError("DF must be defined and not null!")
        with open(file_path, "wb") as pickle_file:
            pickle.dump(df_input, pickle_file)
        with open(txt_file_path, "w") as text_file:
            text_file.write(pickle.format_version)
        
        return df_input

    else:
        with open(txt_file_path, "r") as text_file:
            expected_ver = text_file.read()
        if expected_ver != pickle.format_version: 
            raise AssertionError("Mismatch expected pickle version {} vs installed pickle version {}".format(expected_ver, pickle.format_version))
        else:
            with open(file_path, "rb") as pickle_file:
                return pd.read_pickle(pickle_file)


def df_filterer(df_input: pd.DataFrame, col_name: str, src_regex_text_preproces: None or str, 
                whitelisted_value=None, alpha_lower:bool=False, whitelist: bool=True, drop_temp_col: bool=False):

    if src_regex_text_preproces not in [None, "white_remove", "alphanum"]:
        raise AssertionError("The variable src_regex_text_preprocess gets unknown params!")
    
    if whitelisted_value is None:
        return df_input

    col_name_copy = col_name + "_copy"
    
    df_input[col_name_copy] = df_input[col_name]

    if alpha_lower:
        df_input[col_name_copy] = df_input[col_name_copy].str.lower()

    if src_regex_text_preproces == "white_remove":
        df_input[col_name_copy] = df_input[col_name_copy].str.replace(r"\s", "", regex=True)
    elif src_regex_text_preproces == "alphanum":
        df_input[col_name_copy] = df_input[col_name_copy].str.replace(r"[^a-z0-9]", "", regex=True)

    try: 
        iterator = iter(whitelisted_value) 
    except TypeError as e: 
        print(e)

    if isinstance(whitelisted_value, str):
        df_filtered_index = df_input[df_input[col_name_copy].str.contains(whitelisted_value)].index
    else:
        df_filtered_index = df_input[df_input[col_name_copy].isin(whitelisted_value)].index

    if not(whitelist):
        df_filtered_index = df_input.index.difference(df_filtered_index)
    
    if drop_temp_col:
        df_input.drop(columns=col_name_copy, inplace=True)
    
    df_filtered = df_input.loc[df_filtered_index, :]

    return df_filtered
