import re
import pickle

import pandas as pd
from datetime import datetime as dt


def parse_prefix(string_dt: str, fmt: str):
    """
    It tries to parse the string to datetime,
    and if it fails, it removes the last character based on error messagea & tries again

    input:
        >> string_dt (str) : the string to parse as datetime
        >> fmt (str): The datetime format to be parsed of the string_dt
    output: the parsed datetime object
    """
    try:
        t = dt.strptime(string_dt, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            string_dt = string_dt[:-(len(v.args[0]) - 26)]
            t = dt.strptime(string_dt, fmt)
        else:
            raise
    return t


def dt_str_stamp_lin(start_ts: str or dt, end_ts: str or dt, text: str or list, time_format: str="%H:%M:%S"):
    """
    It takes a start and end timestamp, and a text, and returns a list of tuples of start and end time for
    each partitions in the text
    the partition is defined as follows:
        if its "text" type a string, then a partition is a "word", or whitespace-splitted tokens
        it its "text" type a list, then a partition means a element in that given list

    input:
        >> start_ts (str or datetime class): the start timestamp of the a given text
        >> end (str or datetime class): the end timestamp of the a given text
        >> text (str or list): the text to be partitioned its timestamp
        >> time_format (str, optional): the format of the time string, defaults to %H:%M:%S
    output: a tuple containing datetime partition stamp, its boundary character position detected, and the corresponding cleaned text
    """

    #automatically adds time_format with decimals
    if not time_format.endswith(r"%f"):
        time_format += ".%f"

    #change start_ts and end_ts dtype to datetime format using parse_prefix (remove unconverted data at suffix)
    if isinstance(start_ts, str):
        start_ts = parse_prefix(start_ts, time_format)
    if isinstance(end_ts, str):
        end_ts = parse_prefix(end_ts, time_format)

    #partition by word (whitespace splitted) from a given text
    if isinstance(text, str):
        #cleanse double white-space
        text = re.sub(r"\s+", r" ", text.strip())
        partition_boundary_char_pos = [(ele.start()+1, ele.end()+1) for ele in re.finditer(r'\S+', text)]
        text_len = len(text)

    #partition by each element in a list
    else:
        partition_boundary_char_pos, sum_len = list(), 0
        #example: ["saya", "makan", "nasi"]
        #expected output positions: [1, 5], [6, 11], [12, 16]
        for text_partition in text:
            text_partition = re.sub(r"\s+", r" ", text_partition.strip())
            if len(partition_boundary_char_pos) == 0: #start of the list
                start_pos = 1
                partition_boundary_char_pos.append((start_pos, len(text_partition)+start_pos))
            else:
                skip_whitespace = 1
                start_pos = partition_boundary_char_pos[-1][1] + skip_whitespace
                partition_boundary_char_pos.append((start_pos, len(text_partition)+start_pos))
            sum_len += len(text_partition)
        text_len = (len(text)-1) + sum_len

    #get timestamp of a char
    def lin_char_pos_dt_stamp(char_pos):
        # stamp = dt.strptime(start_ts, time_format) + (dt.strptime(end_ts, time_format) - dt.strptime(start_ts, time_format))*(char_pos-1)/text_len
        stamp = start_ts + (end_ts - start_ts)*(char_pos-1)/text_len
        return dt.strftime(stamp, time_format)

    #get timestamp of boundary char associated with a sentence or token
    partition_dt_stamp = list()
    for start_word_pos, end_word_pos in partition_boundary_char_pos:
        partition_dt_stamp.append((lin_char_pos_dt_stamp(start_word_pos), lin_char_pos_dt_stamp(end_word_pos)))

    return partition_dt_stamp, partition_boundary_char_pos, text


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
            text_file.write("\n")
            text_file.write(f"The pandas package version: {pd.__version__}")

        return df_input

    else:
        #do sanity check on its expected vs installed version
        with open(txt_file_path, "r") as text_file:
            for idx, line in enumerate(text_file.readlines()):
                expected_pkg_ver = re.search("(?<=:).+", line).group(0).strip()
                # expected first line: pickle package version
                if idx == 0 and expected_pkg_ver != pickle.format_version:
                    raise AssertionError("Mismatch expected pickle version {} vs installed pickle version {}".format(expected_pkg_ver, pickle.format_version))
                if idx == 1 and expected_pkg_ver != pd.__version__:
                    raise AssertionError("Mismatch expected pandas version {} vs installed pandas version {}".format(expected_pkg_ver, pd.__version__))

        #if succeed the check, read the actual pickled pandas df file
        with open(file_path, "rb") as pickle_file:
            return pickle.load(pickle_file)


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
