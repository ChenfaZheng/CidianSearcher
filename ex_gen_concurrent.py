from searchercore import Searcher

# to check if file exists
import os

# to generate a excel file with all words in dictionary
import pandas as pd

# to show progress bar
from tqdm import tqdm



MDX_PATH = r'PATH/TO/YOUR/DICT.mdx'
assert os.path.exists(MDX_PATH)


searcher = Searcher(MDX_PATH)

df = pd.DataFrame(
    #         键      词条拼音   词性  拼音   解释   例句原文   例句
    columns=['key', 'pinyin', 'cy', 'py', 'js', 'lj_raw', 'lj']
)



# filter out single character
items = [k.decode() for k, _ in searcher.get_items() if len(k.decode()) > 1]

# iter all words
ctr = 0
ctr_saver = 0
N = len(items)
for key in tqdm(
    iterable=items, 
    total=N, 
):
    res = searcher.gen_tab(key)

    # parse res to dataframe
    for context in res[1:]:
        pinyin = context[0]
        tmp_cx_lst = []
        tmp_res_lst = []
        for cx, py, js, lj_raw in context[1:]:
            if (cx is not None) and (cx not in tmp_cx_lst):
                tmp_cx_lst.append(cx)
            if lj_raw is not None:
                lj = lj_raw.replace('～', key)
            tmp_res_lst.append([key, pinyin, cx, py, js, lj_raw, lj])
        if len(tmp_cx_lst) > 1: # more than one class of this word
            for this_res_lst in tmp_res_lst:
                df.loc[ctr] = this_res_lst
                ctr += 1
    # temperary save for every 10000 line in excel
    if ctr - ctr_saver > 10000:
        try:
            df.to_excel('./word-tmp.xlsx', index=False)
        except:
            # in case the file is opened
            print('file opened, cannot save')
        ctr_saver = ctr
# finally save
df.to_excel('./word.xlsx', index=False)

