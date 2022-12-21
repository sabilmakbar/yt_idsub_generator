# %%
import pandas as pd
import re
from datetime import datetime as dt
import pickle


def dt_str_stamp_lin(start=None, end=None, text:str or list=None, time_format = "%H:%M:%S"):
    """
    It takes a string of text, and a start and end time, and returns a list of tuples, where
    each tuple contains the start and end time of each word in the text

    To attach string list to its adjacent timestamp

    :param str_pos: the position of the character in the string
    """

    #automatically adds time_format with decimals
    if not time_format.endswith(r"%f"):
        time_format += ".%f"

    #split by whitespace
    if isinstance(text, str):
        #cleanse double white-space
        text = re.sub(r"\s+", r" ", text)
        word_pos = [(ele.start()+1, ele.end()+1) for ele in re.finditer(r'\S+', text)]
        text_len = len(text)
    #split by list len
    else:
        word_pos = list()
        #example: ["saya", "makan", "nasi"]
        #expected output: [1, 5], [7,]
        for text_partition in text:
            if len(word_pos) == 0: #start of the list
                start_pos = 1
                word_pos.append((start_pos, len(text_partition)+start_pos))
            else:
                skip_whitespace = 1
                start_pos = word_pos[-1][1] + skip_whitespace
                word_pos.append((start_pos, len(text_partition)+start_pos))
        text_len = (len(text)-1) + len("".join(text))

    word_dt_stamp = list()

    def lin_pos_dt_stamp(str_pos):
        stamp = dt.strptime(start, time_format) + (dt.strptime(end, time_format) - dt.strptime(start, time_format))*(str_pos-1)/text_len
        return dt.strftime(stamp, time_format+r".%f")

    for start_word_pos, end_word_pos in word_pos:
        word_dt_stamp.append((lin_pos_dt_stamp(start_word_pos), lin_pos_dt_stamp(end_word_pos)))

    return word_dt_stamp, word_pos, text


def iter_to_df_creator(*args):
    """
    It takes in an arbitrary number of arguments, the first of which is a list of column names, and the
    rest of which are lists of values. It then returns a dataframe with the column names and values
    input:
        >> *args: iterables, with first value being the list of column names, and next to last values being the values stored
    output: A dataframe with the column names and values
    """
    #first argument for column name, second and later for columns
    col_names = args[0]
    values = args[1:]

    return pd.DataFrame(dict(zip(col_names, values)))


def df_pickler(file_path: str, actions: str, df_input=None):
    """
    > This function is a wrapper for the pickle library that allows you to save and load pandas
    dataframes and write its corresponding pickle version used

    input:
        >> file_path (str): The path to the file you want to dump or load
        >> actions (str): whether to "dump" or "load" dataframe from/to pickle
        >> df_input: The dataframe to be pickled, necessary if action="dump"
    output: A dataframe if "load" or a None if "dump" (returns pickle file & corresponding pickle and pandas format version)
    """
    if actions not in ["load", "dump"]: raise AssertionError("Actions Incorrect! Must be either 'dump' or 'load'!")

    txt_file_path = file_path[:-4]+".txt"
    if actions == "dump":
        if df_input is None or not isinstance(df_input, pd.DataFrame):
            raise AssertionError("DF must be defined and not null!")
        with open(file_path, "wb") as pickle_file:
            pickle.dump(df_input, pickle_file)
        with open(txt_file_path, "w") as text_file:
            text_file.write(f"The pickle package version: {pickle.format_version}")
            text_file.write("/n")
            text_file.write(f"The pandas package version: {pd.__version__}")

        return df_input

    else:
        with open(txt_file_path, "r") as text_file:
            expected_ver = text_file.read()
        if expected_ver != pickle.format_version: 
            raise AssertionError("Mismatch expected pickle version {} vs installed pickle version {}".format(expected_ver, pickle.format_version))
        else:
            with open(file_path, "rb") as pickle_file:
                return pd.read_pickle(pickle_file)


def df_filterer(df_input: pd.DataFrame, col_name: str, src_regex_text_preproces: None or str, whitelisted_value=None, alpha_lower:bool=False, whitelist: bool=True, drop_temp_col: bool=False):
    """
    It filters a dataframe based on a column name, a regex text preprocessing, a whitelisted value, a
    boolean for lowercase, a boolean for whitelist, and a boolean for dropping the temporary column

    input:
        >> df_input (pd.DataFrame): the dataframe you want to filter
        >> col_name (str): the name of the column you want to filter on
        >> src_regex_text_preproces (None or str): params on how the text column is preprocessed and filtered. Choices: None, "white_remove", "alphanum"
        >> whitelisted_value (str or Iterables): the value that you want to filter by
        >> alpha_lower (bool, optional): lowercase the alphabet chars, defaults to False
        >> whitelist (bool, optional): whether to do whitelist filter or blacklist filter as its complement, default to True (use regex as whitelist)
        >> drop_temp_col (bool, optional): if True, the temporary column created for the filtering will be dropped, defaults to False
    output: A filtered dataframe
    """

    if src_regex_text_preproces not in [None, "white_remove", "alphanum"]:
        raise AssertionError("The variable src_regex_text_preprocess gets unknown params!")

    if whitelisted_value is None:
        return df_input

    col_name_copy = col_name + "_copy"

    df_input[col_name_copy] = df_input[col_name].astype("str")

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
    elif whitelisted_value is not None:
        df_filtered_index = df_input[df_input[col_name_copy].isin(whitelisted_value)].index

    if not(whitelist):
        df_filtered_index = df_input.index.difference(df_filtered_index)

    if drop_temp_col:
        df_input.drop(columns=col_name_copy, inplace=True)

    df_filtered = df_input.loc[df_filtered_index, :]

    return df_filtered
