from utils import get_langdetect_result
from config import langdetect_prior_map, langdetect_interest_list

from config import low_memory_cfg
from ftlangdetect import detect

# %%
text_test = "this text is created sebagai acuan dari para el modulo donc je voudrais remercier"
get_langdetect_result(text_test, lang_of_interest=langdetect_interest_list)

# %%
from langdetect import detect_langs
detect_langs(text_test)

# %%