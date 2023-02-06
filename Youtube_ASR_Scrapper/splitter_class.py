import re

import pandas as pd

from nnsplit import NNSplit


try:
    from utils.general_utils import dt_str_stamp_lin
    from utils.txt2int import text2int
except ImportError:
    from .utils.general_utils import dt_str_stamp_lin
    from .utils.txt2int import text2int

class TextSplitter():
    def __init__(self, splitter: NNSplit=None, lang="en"):
        """
        The function takes in a splitter and a language format for splitter.
        If the splitter is None, then it loads the NNSplit

        input:
            >> splitter (NNSplit class): The splitter to use. If None, the default NNSplit is used
            >> lang (str, optional): The language of the text to be tokenized, defaults to en (english)
        """

        if splitter is None:
            splitter = NNSplit

        self.splitter = splitter.load(lang)

    #Clean doubled whitespace or more
    def __text_clean_consecutive_whitespace(self, text_input: str):
        """
        It takes a string as input, and returns a string with all consecutive whitespace characters
        replaced with a single space

        input:
            >> text_input (str): The text to be cleaned
        output:
            The text is being returned with the consecutive whitespace removed.
        """
        return re.sub(r"\s+", r" ", text_input.encode('ascii', errors='ignore').decode()).strip()

    #Split String to Sentences using NNSplitter model
    def split_sentence(self, text_input: str):
        """
        It splits a given string into a list of sentences based on NNSplitter

        input:
            >> text_input (str): The text to be split into sentences list
        output:
            A list of strings, containing sentence per list entry.
        """

        text_input = self.__text_clean_consecutive_whitespace(text_input)
        splitted_iter = self.splitter.split([text_input])[0]

        return [str(split).strip() for split in splitted_iter]

    #Obtain word-level stamp from start and end timestamp
    def word_time_stamp(self, start:str, end:str, text_input:str, time_format = "%H:%M:%S"):
        """
        It takes a start time, end time, and text input, and returns a dictionary with the keys "ts",
        "word_pos", and "text"

        input:
            >> start (str): the start time of the video
            >> end (str): the end time of the video
            >> text_input (str): the text you want to split into words
            >> time_format (str, optional): the format of the time stamps, defaults to %H:%M:%S
        output:
            A dictionary with the keys "ts", "char_pos", and "text" and values of the output from "dt_str_stamp_lin"
        """
        names = ["ts", "char_pos", "text"]
        data = dt_str_stamp_lin(start, end, self.__text_clean_consecutive_whitespace(text_input), time_format)

        return dict(zip(names, data))

    #Obtain sentence-level stamp from start and end timestamp
    def sentence_time_stamp(self, start: str, end: str, text_input: str or list, time_format: str="%H:%M:%S", split_result=False):
        """
        The function returns a list of tuples, where each tuple contains the start and end time of the
        sentence, given text_input as string (which will be checked on sentence boundary by NNSPlitter)
        or list (preserved as it is without NNSplitter), start timestamp of text prompt, end timestamp of text prompt
        its timestamp format, and option to split the start and end splitted timestamp into different list (tuple of lists instead of list of tuples)

        input:
            >> start (str): the start time of a timestamp of given "text_input"
            >> end (str): the end time of the video
            >> text_input (str or list): the text to be time-stamped
            >> time_format (str, optional): format of timestamp input, as per datetime format, defaults to %H:%M:%S
            >> split_result (bool, optional): if True, the result will be split into two lists, one for start time and one for end time, defaults to False (optional)
        output: timestamp splitted from given inputs
        """

        #assuming all list input is already formed as sentence
        if isinstance(text_input, str):
            text_splitted = self.split_sentence(text_input)
        else:
            text_splitted = text_input

        ts, *_ = dt_str_stamp_lin(start, end, text_splitted, time_format)

        if split_result:
            return [ts_start for ts_start, _ in ts], [ts_stop for _, ts_stop in ts]
        else:
            return ts

    #Convert string-based numbers into numbers
    def post_process_text_to_int_sentence(self, text_input: str or list, convert_text_to_int: bool=True):
        """
        Do a prepcoess of changing text number to corresponding integer (in English lang)
        - If the input is a list, then apply the function to each element of the list.
        - If the input is a string, then apply the function to the string.
        - If the input is neither a list nor a string, then raise an error

        input:
            text_input (str or list): text input to be processed
        output:
            >> processed text_input: str or list, depends on input dtype
        """

        def join_splitted_num(text:str):
            return re.sub(r'(\d)\s+(\d)', r'\1\2', text)

        # determine if the function text2int is used
        text2int_fun = text2int if convert_text_to_int else (lambda text: text)

        #check if the text_input is an iterable
        if not isinstance(text_input, str):
            try:
                iter(text_input)
            except TypeError as e:
                pass
            else:
                return [text2int_fun(join_splitted_num(str(val))).strip() for val in text_input]
        else:
            #cast it into a string
            try:
                str(text_input)
            except Exception as e:
                print(e)
            else:
                return text2int_fun(join_splitted_num(str(text_input))).strip()

    #Return second-difference of two timestamps
    def _return_seconds_diff(self, start_ts: str, stop_ts: str):
        return (pd.to_datetime(stop_ts)-pd.to_datetime(start_ts)).total_seconds()

    #Split DF of YT subtitles with Timestamps
    def split_yt_subtitles(self, df_input: pd.DataFrame, subtitle_col_name: str,
                            start_stamp_col_name: str, stop_stamp_col_name: str,
                            thres_no_voice_s: int=5, thres_speech_duration: int=20,
                            convert_text_to_int: bool=True):

        input_colnames = [subtitle_col_name, start_stamp_col_name, stop_stamp_col_name]
        if not all(colname in df_input.columns for colname in input_colnames):
            raise AssertionError("Input colnames isn't found on DF!")

        text_output_list, ts_start_output_list, ts_stop_output_list = list(), list(), list()

        if df_input.shape[0]==0:
            return None, None, None

        text_appended = str(df_input.loc[df_input.index[0], subtitle_col_name])
        start_ts = str(df_input.loc[df_input.index[0], start_stamp_col_name])
        stop_ts = str(df_input.loc[df_input.index[0], stop_stamp_col_name])
        sentence_speech_duration = self._return_seconds_diff(start_ts, stop_ts)

        if df_input.shape[0]==1:
            sentences = self.post_process_text_to_int_sentence(text_input = self.split_sentence(text_appended), convert_text_to_int = convert_text_to_int)
            ts_start_list, ts_stop_list = self.sentence_time_stamp(start_ts, stop_ts, sentences, split_result=True)
            return sentences, ts_start_list, ts_stop_list

        for idx in range(1, df_input.shape[0]):
            curr_idx_data = df_input.loc[df_input.index[idx], :]

            #get sentence speech duration (its initial timestamp to end of speech timestamp)

            if (idx+1 < df_input.shape[0]):
                next_idx_data = df_input.loc[df_input.index[idx+1], :]
                no_voice_seconds_diff = self._return_seconds_diff(str(curr_idx_data[stop_stamp_col_name]), str(next_idx_data[start_stamp_col_name]))

                #readjust sentence speech duration with no_voice_seconds_diff due to some subtitle in a sentence might got splitted
                sentence_speech_duration -= no_voice_seconds_diff

            else: #end of row, set seconds_diff as None
                no_voice_seconds_diff = None

            text_appended = (text_appended + " " + str(curr_idx_data[subtitle_col_name])).strip()
            sentences = self.split_sentence(text_appended)

            stop_ts = str(curr_idx_data[stop_stamp_col_name])
            sentence_speech_duration = self._return_seconds_diff(start_ts, stop_ts)

            if no_voice_seconds_diff is None or no_voice_seconds_diff > thres_no_voice_s or sentence_speech_duration > thres_speech_duration or len(sentences)>1:
                ts_start_list, ts_stop_list = self.sentence_time_stamp(start_ts, stop_ts, sentences, split_result=True)

                #taking last element of splitted text and timestamp as new start if split is found, since it might be correlated with next row in DF
                if (idx+1 < df_input.shape[0]) and len(sentences)>1:
                    text_output_list.extend(self.post_process_text_to_int_sentence(text_input = sentences[:-1], convert_text_to_int = convert_text_to_int))
                    ts_start_output_list.extend(ts_start_list[:-1])
                    ts_stop_output_list.extend(ts_stop_list[:-1])

                    #assigning last entry of list as new start
                    start_ts = str(ts_start_list[-1])
                    sentence_speech_duration = self._return_seconds_diff(start_ts, str(ts_stop_list[-1]))
                    text_appended = str(sentences[-1])

                else: #either last data or cutted due to duration-related threshold
                    text_list = self.post_process_text_to_int_sentence(text_input = sentences, convert_text_to_int = convert_text_to_int)

                    text_output_list.extend(text_list)
                    ts_start_output_list.extend(ts_start_list)
                    ts_stop_output_list.extend(ts_stop_list)

                    if (idx+1 < df_input.shape[0]): #taking next row as new start timestamp and None as text_appended
                        start_ts = str(next_idx_data[start_stamp_col_name])
                        sentence_speech_duration = 0
                        text_appended = ""

        return text_output_list, ts_start_output_list, ts_stop_output_list
