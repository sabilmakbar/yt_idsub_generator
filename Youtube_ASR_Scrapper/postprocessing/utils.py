import re
from langdetect.detector_factory import DetectorFactory, PROFILES_DIRECTORY
from langdetect.lang_detect_exception import LangDetectException

def assert_text_type(text):
    """
    > This function checks if the input is a string, int, float, or None. If it's not, it raises a
    TypeError. If it is, it returns the input
    
    :param text: The text to be converted into speech
    :return: the text variable, which is either a string, None, int, or float.
    """
    NoneType = type(None)
    if not isinstance(text, (str, NoneType, int, float)):
        raise TypeError(f"Received var type of {type(text).__name__}, expected either of 'str', 'int', 'float', or None!")
    if isinstance(text, (int, float)): #cast into str
        text = str(text)
    return text


def bracket_balancer(text: str):
    """
    It takes a string as input, and returns a string with balanced brackets 
    The balanced bracket is placed adjacent to exactly one word enclosed by unclosed bracket
    Doesn't consider recursively unbalanced bracket

    Input:
        text (str)
    Output:
        The text with the brackets balanced.
    """
    bracket_pair_list = [("(", ")"), ("{", "}"), ("[", "]")]
    text = assert_text_type(text)
    for br_open, br_close in bracket_pair_list:
        #balance the brackets
        #1: fix unopened bracket
        if re.search(f"^[^\{br_open}]*(?<=\{br_close})", text):
            text_modified = re.sub("(^|\s)(\S*(?<=\]))", r"\1[\2", text)
        #1: fix unclosed bracket
        elif re.search(f"(?=\{br_open})[^\{br_close}]*$", text):
            text_modified = re.sub("((?=\[)\S*)(\s|$)", r"\1]\2", text)
        else:
            text_modified = text
    return text_modified


def detect_non_ascii(text: str):
    text = assert_text_type(text)
    return re.findall(r'([^\x00-\x7F]+)', text) if text is not None else []


def get_text_in_brackets(text: str, bracket_pair_list: list=[("(", ")"), ("{", "}"), ("[", "]")], pat_to_excl: list=None, return_distinct: bool=False):
    """
    It takes a string and returns a list of strings that are enclosed in brackets

    Input:
        text (str): the text to be searched
        par_list (list of tuple pair, default = [("(", ")"), ("{", "}"), ("[", "]")]): list of tuples of opening and closing brackets
        pat_to_excl (list, default None): pattern enclosed in tuples that wanted to be excluded (useful for avoiding token caught)
    Output:
        A list of lists of strings that are enclosed in brackets (list of ragged lists that has the len of n-pairs of brackets x pattern caught).
    """
    NoneType = type(None)
    text = assert_text_type(text)
    for _var, _var_type, _arg_name in zip((bracket_pair_list, pat_to_excl, return_distinct), (list, (list, NoneType), bool), ("bracket_pair_list", "pat_to_excl", "return_distinct")):
        if (not isinstance(_var,_var_type)):
            raise TypeError(f"Arg passed type is unexpected for var {_arg_name}! Expected {_var_type.__name__} received {type(_var).__name__}!")

    if text is not None:
        text = bracket_balancer(text)
        result_list = [re.findall(f"\{open_chr}[^\{close_chr}]*\{close_chr}", text) for open_chr, close_chr in bracket_pair_list]
    else:
        result_list = [[] for _ in range(len(bracket_pair_list))]

    if pat_to_excl is not None and len(pat_to_excl) > 0 and text is not None:
        for idx, result_par_encl in enumerate(result_list):
            result_list[idx] = [caught_text for caught_text in result_par_encl if caught_text not in pat_to_excl]

    if return_distinct:
        return [list(set(result)) for result in result_list]
    else:
        return result_list


def delete_text_in_unbalanced_brackets(text: str, bracket_pair_list: list=[("(", ")"), ("{", "}"), ("[", "]")], text_within_to_exclude: list=[]):
    """
    It takes a string and returns a list of strings that are cleaned from enclosed in brackets
    
    Input:
        text (str): the text to be searched
        par_list (list of tuple pair, default = [("(", ")"), ("{", "}"), ("[", "]")]): list of tuples of opening and closing brackets
        pat_to_excl (list, default None): pattern enclosed in tuples that wanted to be excluded (useful for avoiding token caught)
    Output:
        A list of lists of strings that are enclosed in brackets (list of ragged lists that has the len of n-pairs of brackets x pattern caught).
    """
    NoneType = type(None)
    text = assert_text_type(text)
    for _var, _var_type, _arg_name in zip((bracket_pair_list, text_within_to_exclude), (list, list), ("bracket_pair_list", "text_within_to_exclude")):
        if (not isinstance(_var,_var_type)):
            raise TypeError(f"Arg passed type is unexpected for var {_arg_name}! Expected {_var_type.__name__} received {type(_var).__name__}!")

    if text is not None:
        #create pat of component "\s*\[\s*" "{text_pat_a_to_excl}" "\s*\]\s*" and pat of component "\s*\[\s*" "{text_pat_b_to_excl}" "\s*\]\s*" with regex pipe (or logic)
        # pat_within_chars_to_exclude = "|".join(["\s*\[\s*" + text + "\s*\]\s*" for text in text_within_to_exclude])
        #encapsulate pat_within on a capturing group (to make it repeating) then capsulate those in capturing group
        # re_to_excl = ""+

        # # var_1:
        # (\[+[^\[]*) ((?:\s*\[sen\]\s*|\s*\[tok\]\s*)+)([^\]]*\]+)
        # # var_2:
        # (\[+[^\[]*)(?:(?:([^\[\]]*?)(\s*?\[sen\]\s*?)+?([^\[\]]*?)|([^\[\]]*?)(\s*?\[tok\]\s*?)+?([^\[\]]*?))+)([^\]]*\]+)

        for br_open, br_close in bracket_pair_list:
            #detect all text within the bracket(s)
            re_to_get_bracket_pair_list = f"\{br_open}([^\{br_open}]*?)\{br_close}"
            # (?:\{br_open}+|\s)(.*?)(?:\{br_close}+\s)
            while True:
                #balance the brackets
                text = bracket_balancer(text)
                text_caught = re.findall(re_to_get_bracket_pair_list, text)

                #short circuit escape infinite loop, means text are completely cleansed
                if sum([1 for pat in text_caught if pat not in text_within_to_exclude]) == 0:
                    break

                pat_text_to_remove = "|".join([re.escape(pat) for pat in text_caught if pat not in text_within_to_exclude])
                re_to_remove_text_inside_bracket = f"\{br_open}(?:{pat_text_to_remove})\{br_close}"
                # f"(?:\{br_open}+|\s)(?:{pat_text_to_remove})(?:\{br_close}+\s)"
                text = re.sub(re_to_remove_text_inside_bracket, "", text)

        return text


def remove_non_ascii(text: str):
    text = assert_text_type(text)
    return re.sub(r'([^\x00-\x7F]+)', ' ', text) if text is not None else None


# def list_iterator_text_cleanser(text_list: list, concat_to_str: bool=False, separator: str=None, default_str_value):
#     NoneType = type(None)
#     for _var, _var_type, _arg_name in zip((text_list, concat_to_str, separator), ((list, NoneType), bool, (str, NoneType)), ("text_list", "concat_to_str", "separator")):
#         if (not isinstance(_var,_var_type)):
#             raise TypeError(f"Arg passed type is unexpected for var {_arg_name}! Expected {_var_type.__name__} received {type(_var).__name__}!")
#     if concat_to_str and separator is None:
#         raise AssertionError("The separator can't be None if the concat_to_str is set as True!")

#     if not_concat_to_str:
#     return 


def _init_langdetect_factory(prior_map: dict=None, seed: int=100):
    """
    It creates a detector object that will be used to detect the language of a given text
    
    Input:
        prior_map_res (dict): Prior map probability distribution as init state for langdetect
    :type prior_map_res: dict
    :return: A detector object.
    """

    if prior_map is not None and not isinstance(prior_map, dict):
        raise TypeError(f"Unexpected type of langdetect factory 'prior_map'! Expected 'dict', received {type(prior_map).__name__}!")

    # global factory_detector
    # if factory_detector is None:
    factory_detector = DetectorFactory()
    factory_detector.load_profile(PROFILES_DIRECTORY)
    factory_detector.seed = seed

    detector = factory_detector.create()

    if prior_map is not None:
        detector.set_prior_map(prior_map)

    return detector


def get_langdetect_result(text: str, lang_of_interest:list=None, **kwargs):
    
    if not isinstance(text, str):
        raise TypeError(f"Unexpected type of 'text' input! Expected 'str', received {type(text).__name__}!")
    if lang_of_interest is not None and not isinstance(lang_of_interest, list):
        raise TypeError(f"Unexpected type of 'lang_of_interest' input! Expected 'list', received {type(lang_of_interest).__name__}!")

    detector = _init_langdetect_factory(**kwargs)
    #set max length w/ big number to avoid truncation
    detector.set_max_text_length = 10**12
    detector.append(text)

    try:
        dict_res = {}
        list_res = detector.get_probabilities()
    except LangDetectException: #no valid text to catch
        pass
    else:
        for res in list_res:
            dict_res[res.__repr__()[:2]] = float(res.__repr__()[3:])

    if lang_of_interest is not None and len(lang_of_interest) > 0:
        #only collect relevant lang of interest
        dict_output = dict()
        for lang in lang_of_interest:
            dict_output[lang] = dict_res.get(lang, 0)
        dict_output["others"] = 1-sum(dict_output.values())
        return dict_output
    else:
        #return result of langdetect as it is
        return dict_res
