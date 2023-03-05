import re
import types
import warnings
from collections import Iterable

from langdetect.detector_factory import DetectorFactory, PROFILES_DIRECTORY
from langdetect.lang_detect_exception import LangDetectException


def none_val_warning(warning_text):
    """
    If the value of the variable is None, then print a warning message.

    Input:
        warning_text: The text to be displayed in the warning
    Output:
        A warning object with category of 'RuntimeWarning'
    """

    warnings.warn(warning_text, category=RuntimeWarning)


def _assert_text_type(text):
    """
    > This function checks if the input is a string, int, float, or None. If it's not, it raises a
    TypeError. If it is not a None, it returns the input. If None, it returns a warning.

    Input:
        text: The var checked to text-castable format
    Output:
        str-casted text variable
    """

    if text is None:
        none_val_warning("The text input to '_assert_text_type' is None!")
    elif not isinstance(text, (str, int, float)):
        raise TypeError(f"Received var type of {type(text).__name__}, expected either of 'str', 'int', 'float'!")

    #return casted str obj
    return str(text).strip()


def bracket_balancer(text: str):
    """
    It takes a string as input, and returns a string with balanced brackets 
    The balanced bracket is placed adjacent to exactly one word enclosed by unclosed bracket
    Doesn't consider recursively unbalanced bracket

    Input:
        text (str): the text to be bracket-balanced
    Output:
        The text with the brackets balanced.
    """

    bracket_pair_list = [("(", ")"), ("{", "}"), ("[", "]")]
    text = _assert_text_type(text)
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

    return text_modified.strip()


def detect_non_ascii(text: str):
    """
    It returns a list of all non-ASCII characters in the given text

    Input:
        text (str): text to be checked its non-ASCII chars
    Output:
        A list of all non-ascii characters in the text.
    """

    text = _assert_text_type(text)
    return re.findall(r'([^\x00-\x7F]+)', text) if text is not None else []


def get_text_in_brackets(text: str, bracket_pair_list: list=[("(", ")"), ("{", "}"), ("[", "]")], pat_to_excl: list=[], return_distinct: bool=False):
    """
    It takes a string and returns a list of strings that are enclosed in brackets

    Input:
        text (str): the text to be searched
        par_list (list of tuple pair, default = [("(", ")"), ("{", "}"), ("[", "]")]): list of tuples of opening and closing brackets
        pat_to_excl (list, default empty list "[]"): pattern enclosed in tuples that wanted to be excluded (useful for avoiding token caught)
    Output:
        A list of lists of strings that are enclosed in brackets (list of ragged lists that has the len of n-pairs of brackets x pattern caught).
    """

    text = _assert_text_type(text)
    for _var, _var_type, _arg_name in zip((bracket_pair_list, pat_to_excl, return_distinct), (list, list, bool), ("bracket_pair_list", "pat_to_excl", "return_distinct")):
        if (not isinstance(_var,_var_type)):
            raise TypeError(f"Arg passed type is unexpected for var '{_arg_name}'! Expected {_var_type.__name__}, received {type(_var).__name__}!")

    if text is not None:
        text = bracket_balancer(text)
        result_list = [re.findall(f"\{open_chr}[^\{close_chr}]*\{close_chr}", text) for open_chr, close_chr in bracket_pair_list]
    else:
        result_list = [[] for _ in range(len(bracket_pair_list))]

    if len(pat_to_excl) > 0 and text is not None:
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
        bracket_pair_list (list of tuple pair, default = [("(", ")"), ("{", "}"), ("[", "]")]): list of tuples of opening and closing brackets
        text_within_to_exclude (list, default empty list "[]"): pattern enclosed in brackets that wanted to be excluded (useful for avoiding token caught)
    Output:
        A list of lists of strings that are enclosed in brackets (list of ragged lists that has the len of n-pairs of brackets times pattern caught).
    """

    text = _assert_text_type(text)
    for _var, _var_type, _arg_name in zip((bracket_pair_list, text_within_to_exclude), (list, list), ("bracket_pair_list", "text_within_to_exclude")):
        if (not isinstance(_var,_var_type)):
            raise TypeError(f"Arg passed type is unexpected for var '{_arg_name}'! Expected {_var_type.__name__}, received {type(_var).__name__}!")

    if text is not None:
        for br_open, br_close in bracket_pair_list:
            #detect all text within the bracket(s)
            re_to_get_bracket_pair_list = f"\{br_open}([^\{br_open}]*?)\{br_close}"
            #ensure everything is cleansed before escaping the loop
            while True:
                #balance the brackets
                text = bracket_balancer(text)
                text_caught = re.findall(re_to_get_bracket_pair_list, text)

                #short circuit escape infinite loop, means text are completely cleansed
                if sum([1 for pat in text_caught if pat not in text_within_to_exclude]) == 0:
                    break

                pat_text_to_remove = "|".join([re.escape(pat) for pat in text_caught if pat not in text_within_to_exclude])
                re_to_remove_text_inside_bracket = f"\{br_open}(?:{pat_text_to_remove})\{br_close}"
                text = re.sub(re_to_remove_text_inside_bracket, "", text).strip()

        #return text if they're not deleted wholly, else not returning anything (None)
        if text != "":
            return text
        else:
            none_val_warning("Cleansed text from fn 'delete_text_in_unbalanced_brackets' is None!")


def remove_non_ascii(text: str):
    """
    It removes all non-ascii characters from a string

    Input:
        text (str): The text to be cleaned
    Output:
        A string with all non-ascii characters removed.
    """

    text = _assert_text_type(text)
    cleansed_text = re.sub(r'([^\x00-\x7F]+)', '', text).strip() if text is not None else None

    #return text if they're not deleted wholly, else not returning anything (None)
    if cleansed_text != "":
        return cleansed_text
    else:
        none_val_warning("Cleansed text from fn 'remove_non_ascii' is None!")


def iterator_text_fn_applier(fn, iter_obj, raiseNoneObjEval: bool=True, return_iter: bool=True, skip_none_after_cleansed : bool=True, concat_token: str=" "):
    """
    > It applies the function to each element in the iterable object, and returns the iterable object
    with the function applied to each element

    Input:
        fn (any callable obj): will be assumed as the function to be applied to each element in the iterable object
        iter_obj (any iterable except string): the object to be iterated
        raiseNoneObjEval (bool, default True): if the 2nd Argument is None, raise ValueError. If False, return None
        return_iter (bool, default True): the function will return the post-fn applied iterable object. If False, it'll return the concatenated string of post-fn applied obj
        skip_none_after_cleansed (bool, default True): flag whether the None val in cleansed iter needs to be removed
        concat_token (str, default " "): the token to concatenate the iterated object. Default is " " (space)
    Output:
        List or concatted string of the result of the function applied to each element of the iterable object.
    """

    for _obj, _expected_obj_type, _obj_name in zip((raiseNoneObjEval, return_iter, skip_none_after_cleansed, concat_token), (bool, bool, bool, str), ("raiseNoneObjEval", "return_iter", "skip_none_after_cleansed", "concat_token")):
        if not isinstance(_obj, _expected_obj_type):
            raise TypeError(f"Arg passed type is unexpected for var '{_obj_name}'! Expected {_expected_obj_type.__name__}, received {type(_obj).__name__}!")

    if raiseNoneObjEval and iter_obj is None:
        raise ValueError("The 2nd Argument is None while the value 'raiseNoneObjEval' is set True!")
    elif iter_obj is None:
        return None
    else:
        #short circuit, ensure the fn is callable and object is iterable
        #ensure the object is not a Generator, since it'll be called twice (which Generator object couldn't)
        if isinstance(iter_obj, types.GeneratorType):
            raise TypeError("Received 2nd Argument (object to iterate) type as Generator! Store using list() method first since it'll call the iterable twice!")
        if (not isinstance(iter_obj, Iterable)):
            raise TypeError(f"Received 2nd Argument as non-iterable object! Type info: {type(iter_obj).__name__}")
        if isinstance(iter_obj, str):
            raise TypeError("Received 2nd Argument as string!")
        if not callable(fn):
            raise AssertionError(f"The 1st Argument must be callable (can be treated as fn)! Type info: {type(fn).__name__}")

    #ensure and cast all elements in iterable object are castable to string
    str_iter_obj = [_assert_text_type(val) for val in iter_obj]

    #note: the None 'obj' within the 'str_iter_obj' is handled within the 'fn' itself
    obj_after_iterated = [fn(text) for text in str_iter_obj]

    #apply none post-process filtering
    if skip_none_after_cleansed:
        obj_after_iterated = [val.strip() for val in obj_after_iterated if val is not None]
    else:
        #if there's a None value on 'obj_after_iterated', it'll be changed with default empty str ("")
        obj_after_iterated = [val.strip() if val is not None else "" for val in obj_after_iterated]

    if return_iter:
        return obj_after_iterated
    #add whitespace on boundary after trimmed if 'concat_token' isn't whitespace
    elif not re.match("\s+", concat_token):
        return f" {concat_token.strip()} ".join(obj_after_iterated)
    #defaulting 'concat_token' as period + whitespace
    else:
        return ". ".join(obj_after_iterated)


def _init_langdetect_factory(prior_map: dict=None, seed: int=100):
    """
    It creates a detector object that will be used to detect the language of a given text

    Input:
        prior_map_res (dict): Prior map probability distribution as init state for langdetect
        seed (int, default 100): Seed for langdetect_factory object (for reproducibility)
    Output:
        A detector object.
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


def get_langdetect_result(text: str, lang_of_interest:list=[], **kwargs):
    """
    > It takes in a string of text as input, and returns a dictionary of language probabilities from langdetect module

    Input:
        text (str): the text to be analyzed
        lang_of_interest (list, default empty list "[]"): list of language codes to be returned. If empty list, all languages detected will be returned
        **kwargs will be passed into langdetect detector initiation
    Outupt:
        A dictionary of language and its probability.
    """

    text = _assert_text_type(text)
    if not isinstance(lang_of_interest, list):
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

    if len(lang_of_interest) > 0:
        #only collect relevant lang of interest
        dict_output = dict()
        for lang in lang_of_interest:
            dict_output[lang] = dict_res.get(lang, 0)
        dict_output["others"] = 1-sum(dict_output.values())
        return dict_output
    else:
        #return result of langdetect as it is
        return dict_res
