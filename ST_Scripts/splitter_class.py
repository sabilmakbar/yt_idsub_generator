from time import time
import pandas as pd
from nnsplit import NNSplit
from datetime import datetime as dt
import re
import os

try:
    from utils.general_utils import dt_str_stamp_lin
    from utils.txt2int import text2int
except ImportError:
    from .utils.general_utils import dt_str_stamp_lin
    from .utils.txt2int import text2int

class TextSplitter():
    def __init__(self, splitter: NNSplit, lang="en"):
        self.splitter = splitter.load(lang)
        pass

    def text_preprocess(self, text_input: str):
        return re.sub(r"\s+", r" ", text_input).strip()

    def split_sentence(self, text_input: str):
        text_input = self.text_preprocess(text_input)
        splitted_iter = self.splitter.split([text_input])[0]
        
        return [str(split).strip() for split in splitted_iter]

    def word_pos_split_sentence(self, text_input:str, word_start: int=1):
        text_input = self.text_preprocess(text_input)
        pos_start_list = [word_start]
        pos_end_list = []
        splits = self.split_sentence(text_input)
        for idx, text in enumerate(splits):
            num_words = len(text.split(" "))
            if 0 < idx < len(splits)-1:
                pos_start_list.append(pos_start_list[idx]+num_words)
                pos_end_list.append(pos_end_list[idx-1]+num_words)
            elif idx == 0:
                pos_start_list.append(pos_start_list[idx]+num_words)
                pos_end_list.append(num_words)
            else:
                pos_end_list.append(pos_end_list[idx-1]+num_words)
        
        return list(zip(pos_start_list, pos_end_list))
    

    def word_time_stamp(self, start:str, end:str, text_input:str, time_format = "%H:%M:%S"):
        names = ["ts", "word_pos", "text"]
        data = dt_str_stamp_lin(start, end, self.text_preprocess(text_input), time_format)

        return dict(zip(names, data))

    def sentence_time_stamp(self, start: str, end: str, text_input: str, time_format: str="%H:%M:%S", split_result=False):
        ts = dt_str_stamp_lin(start, end, self.text_preprocess(text_input), time_format)[0]
        
        word_pos = self.word_pos_split_sentence(text_input, word_start=0)

        sentence_ts = []
        for start, end in word_pos:
            sentence_ts.append((ts[start-1][0], ts[end-1][1]))

        if split_result:
            return [ts_start for ts_start, _ in sentence_ts], [ts_stop for _, ts_stop in sentence_ts]
        else:
            return sentence_ts

    def post_process_sentence(self, text_input: str or list):
        if not isinstance(text_input, str):
            try: 
                iter(text_input) 
            except TypeError as e:
                pass
            else:
                return [text2int(re.sub(r'(\d)\s+(\d)', r'\1\2', str(val))) for val in text_input]
        
        try:
            str(text_input)
        except Exception as e:
            print(e)
        else:
            return text2int(re.sub(r'(\d)\s+(\d)', r'\1\2', str(text_input)))
        

    def split_yt_subtitles(self, df_input: pd.DataFrame, subtitle_col_name: str, 
                            start_stamp_col_name: str, stop_stamp_col_name: str, thres_s: int=15):

        input_colnames = [subtitle_col_name, start_stamp_col_name, stop_stamp_col_name]
        if not all(colname in df_input.columns for colname in input_colnames):
            raise AssertionError("Input colnames isn't found on DF!")

        text_appended = df_input.loc[df_input.index[0], subtitle_col_name]
        start_ts = df_input.loc[df_input.index[0], start_stamp_col_name]
        stop_ts = df_input.loc[df_input.index[0], stop_stamp_col_name]

        if df_input.shape[0]:
            return text_appended, start_ts, stop_ts
        

        text_output_list = list()
        ts_start_output_list = list()
        ts_stop_output_list = list()

        for idx in range(1, df_input.shape[0]):
            curr_idx_data = df_input.loc[df_input.index[idx], :]
            prev_idx_data = df_input.loc[df_input.index[idx-1], :]
            seconds_diff = (curr_idx_data[start_stamp_col_name]-prev_idx_data[stop_stamp_col_name]).total_seconds()

            if (idx == df_input.shape[0]-1) or seconds_diff > thres_s:
                stop_ts = prev_idx_data[stop_stamp_col_name]
                
                sentences = self.post_process_sentence(self.split_sentence(text_appended))
                ts_start_list, ts_stop_list = self.sentence_time_stamp(start_ts, stop_ts, text_appended, split_result=True)

                text_output_list.append(sentences)
                ts_start_output_list.append(ts_start_list)
                ts_stop_output_list.append(ts_stop_list)

                start_ts = curr_idx_data[start_stamp_col_name]
                text_appended = curr_idx_data[subtitle_col_name]
            
            else:
                text_appended = text_appended + " " + curr_idx_data[subtitle_col_name]

        return text_output_list, ts_start_output_list, ts_stop_output_list

    


