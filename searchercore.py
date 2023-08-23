from readmdict import MDX, MDD
import xmltodict
from random import randint


class Searcher():
    def __init__(self, mdx_path):
        self.mdx = MDX(mdx_path)
        self.items = [*self.mdx.items()]
        # remove items that hase a key starting with '0'
        self.items = [x for x in self.items if not x[0].decode().startswith('0')]
        self.len_items = len(self.items)
        print('\n-------------------')
        print(f'{mdx_path} loaded')
        print(f'Number of items: {self.len_items}')
        print('-------------------\n')
      
    def get_items(self):
        return self.items

    def get(self, mykey, last_key=None) -> str:
        if last_key == mykey:
            return
        
        have_key = False
        for k, v in self.items:
            key = k.decode()
            if key == mykey:
                have_key = True
                break
        if not have_key:
            return 'No such key'
        
        output_page = '====================\n'
        val = v.decode()
        if val.startswith('@@@LINK='):
            real_key = val[8:].strip()
            output_page += f'{key} SAME AS {real_key}\n'
            output_page += self.get(real_key, last_key=mykey)
            return output_page

        context_lst = []
        idx0 = -1
        for idx in range(len(val)):
            if val[idx:idx+6] == '<entry':
                idx0 = idx
            elif val[idx:idx+8] == '</entry>':
                context_lst.append(val[idx0:idx+8])
                idx0 = -1
        
        # remove image tag
        for idx, context in enumerate(context_lst):
            cidx = 0
            while cidx < len(context):
                if context[cidx:cidx+4] == '<img':
                    for cidx1 in range(cidx, len(context)):
                        if context[cidx1] == '>':
                            break
                    context = context[:cidx] + context[cidx1+1:]
                else:
                    cidx += 1
            context_lst[idx] = context

        # remove table tag
        for idx, context in enumerate(context_lst):
            cidx = 0
            while cidx < len(context):
                if context[cidx:cidx+6] == '<table':
                    for cidx1 in range(cidx, len(context)):
                        if context[cidx1-7:cidx1+1] == '</table>':
                            break
                    context = context[:cidx] + context[cidx1+1:]
                else:
                    cidx += 1
            context_lst[idx] = context

        
        for context in context_lst:
            # output_page += f'Context: {context}\n'
            context_dict = xmltodict.parse(context)

            # deal with title
            title_str = ''
            if 'hw' in context_dict['entry']:
                if type(context_dict['entry']['hw']) is str:
                    title_str += f'{context_dict["entry"]["hw"]} '
                else:
                    title_str += f'{context_dict["entry"]["hw"]["#text"]} '
                    if 'pinyin' in context_dict['entry']['hw']:
                        title_str += f'({context_dict["entry"]["hw"]["pinyin"]}) '
            output_page += f'{title_str}\n'

            # deal with defination
            def_lst = context_dict['entry']['def']
            # output_page += f'{def_lst}\n'
            if type(def_lst) is str:
                output_page += f'\t{def_lst}\n'
                continue
            elif type(def_lst) is dict:
                def_lst = [def_lst]
            assert type(def_lst) is list
            

            for def_ in def_lst:
                lingjian = False
                tong = False
                jian = False
                output_str = ''
                output_str += '\t'
                if type(def_) is str:
                    output_str += f'{def_}'
                    output_page += f'{output_str}\n'
                    continue
                if 'num' in def_:
                    output_str += f'{def_["num"]} '
                if 'pinyin' in def_:
                    if '#text' in def_ and '另见' in def_['#text']:
                        lingjian = True
                        lingjian_str = def_['#text']
                        lingjian_split = lingjian_str.split('另见')
                        if len(lingjian_split[-1]) > 0:
                            output_str += f'另见{def_["pinyin"]}{lingjian_split[-1]} '
                    else:
                        output_str += f'({def_["pinyin"]}) '
                if 'ps' in def_:
                    output_str += f'[{def_["ps"]}] '
                if (not lingjian) and ('#text' in def_):
                    if def_['#text'].startswith('同“”'):
                        if type(def_['a']) is list:
                            tmp_str = '、'.join([
                                f'“{x["@href"][8:]}”' for x in def_['a']
                            ])
                            output_str += f'同{tmp_str}{def_["#text"][3:].replace("、", "")} '
                        else:
                            output_str += f'同“{def_["a"]["@href"][8:]}”{def_["#text"][3:]} '
                        tong = True
                    if def_['#text'].startswith('旧同“”'):
                        if type(def_['a']) is list:
                            tmp_str = '、'.join([
                                f'“{x["@href"][8:]}”' for x in def_['a']
                            ])
                            output_str += f'旧同{tmp_str}{def_["#text"][4:].replace("、", "")} '
                        else:
                            output_str += f'旧同“{def_["a"]["@href"][8:]}”{def_["#text"][4:]} '
                        tong = True
                    elif def_['#text'].startswith('见【】'):
                        if type(def_['a']) is list:
                            tmp_str = '、'.join([
                                f'【{x["@href"][8:]}】' for x in def_['a']
                            ])
                            output_str += f'见{tmp_str}{def_["#text"][3:].replace("、", "")} '
                        else:
                            output_str += f'见【{def_["a"]["@href"][8:]}】{def_["#text"][3:]} '
                        jian = True
                    elif def_['#text'].startswith('见〖〗'):
                        if type(def_['a']) is list:
                            tmp_str = '、'.join([
                                f'〖{x["@href"][8:]}〗' for x in def_['a']
                            ])
                            output_str += f'见{tmp_str}{def_["#text"][3:].replace("、", "")} '
                        else:
                            output_str += f'见〖{def_["a"]["@href"][8:]}〗{def_["#text"][3:]} '
                        jian = True
                    elif def_['#text'].startswith('见“”'):
                        if type(def_['a']) is list:
                            tmp_str = '、'.join([
                                f'“"{x["@href"][8:]}”' for x in def_['a']
                            ])
                            output_str += f'见{tmp_str}{def_["#text"][3:].replace("、", "")} '
                        else:
                            output_str += f'见“"{def_["a"]["@href"][8:]}”{def_["#text"][3:]} '
                        jian = True
                    else:
                        output_str += f'{def_["#text"]} '
                if 'ex' in def_:
                    if type(def_['ex']) is list:
                        tmp_str = ''
                        for ex in def_['ex']:
                            if type(ex) is str:
                                tmp_str += f'{ex}'
                            elif type(ex) is dict:
                                tmp_str += f'{ex["#text"]} '
                        output_str += f'{tmp_str} '
                    elif type(def_['ex']) is dict:
                        output_str += f'{def_["ex"]["#text"]} '
                    else:
                        output_str += f'{def_["ex"]} '
                
                output_page += f'{output_str}\n'
        
        # after processing
        if '()' in output_page:
            output_page = output_page.replace('()', '')
        if '[]' in output_page:
            output_page = output_page.replace('[]', '')
        if '（）' in output_page:
            output_page = output_page.replace('（）', '')
        if '【】' in output_page:
            output_page = output_page.replace('【】', '')
        if '〖〗' in output_page:
            output_page = output_page.replace('〖〗', '')
        return output_page
    
    def search(self, mykey) -> None:
        res = self.get(mykey)
        if res == 'No such key':
            print(f'No such key: {mykey}')
        else:
            print(res)

    def search_all(self) -> None:
        for k, v in self.items:
            key = k.decode()
            print(f'Key: {key}')
            self.search(key)
    
    def gen_tab(self, mykey) -> list:
        
        have_key = False
        for k, v in self.items:
            key = k.decode()
            if key == mykey:
                have_key = True
                break
        if not have_key:
            return []
        
        output_page = '====================\n'
        val = v.decode()
        if val.startswith('@@@LINK='):
            # real_key = val[8:].strip()
            # output_page += f'{key} SAME AS {real_key}\n'
            # print(output_page)
            # return self.gen_tab(real_key, last_key=mykey)
            return []

        context_lst = []
        idx0 = -1
        for idx in range(len(val)):
            if val[idx:idx+6] == '<entry':
                idx0 = idx
            elif val[idx:idx+8] == '</entry>':
                context_lst.append(val[idx0:idx+8])
                idx0 = -1
        
        # remove image tag
        for idx, context in enumerate(context_lst):
            cidx = 0
            while cidx < len(context):
                if context[cidx:cidx+4] == '<img':
                    for cidx1 in range(cidx, len(context)):
                        if context[cidx1] == '>':
                            break
                    context = context[:cidx] + context[cidx1+1:]
                else:
                    cidx += 1
            context_lst[idx] = context

        # remove table tag
        for idx, context in enumerate(context_lst):
            cidx = 0
            while cidx < len(context):
                if context[cidx:cidx+6] == '<table':
                    for cidx1 in range(cidx, len(context)):
                        if context[cidx1-7:cidx1+1] == '</table>':
                            break
                    context = context[:cidx] + context[cidx1+1:]
                else:
                    cidx += 1
            context_lst[idx] = context
        
        res_lst_all = [key, ]
        
        for context in context_lst:
            context_dict = xmltodict.parse(context)

            res_lst = [None, ]

            # deal with title
            title_str = ''
            if 'hw' in context_dict['entry']:
                if not type(context_dict['entry']['hw']) is str:
                    if 'pinyin' in context_dict['entry']['hw']:
                        res_lst[0] = f'{context_dict["entry"]["hw"]["pinyin"]}'

            output_page += f'{title_str}\n'

            # deal with defination
            def_lst = context_dict['entry']['def']
            # output_page += f'{def_lst}\n'
            if type(def_lst) is str:
                res_lst_all.append(res_lst)
                continue
            elif type(def_lst) is dict:
                def_lst = [def_lst]
            assert type(def_lst) is list
            

            for def_ in def_lst:
                this_res_lst = [
                    None, # cixing
                    None, # pinyin
                    None, # shiyi
                    None, # liju
                ]
                if type(def_) is str:
                    this_res_lst[2] = def_
                    res_lst.append(this_res_lst)
                    continue
                # if 'num' in def_:
                #     output_str += f'{def_["num"]} '
                if 'pinyin' in def_:
                    this_res_lst[1] = f'{def_["pinyin"]}'
                if 'ps' in def_:
                    this_res_lst[0] = f'{def_["ps"]}'
                if '#text' in def_:
                    this_res_lst[2] = f'{def_["#text"]}'
                if 'ex' in def_:
                    if type(def_['ex']) is list:
                        tmp_str = ''
                        for ex in def_['ex']:
                            if type(ex) is str:
                                tmp_str += f'{ex}'
                            elif type(ex) is dict:
                                tmp_str += f'{ex["#text"]} '
                        this_res_lst[3] = tmp_str
                    elif type(def_['ex']) is dict:
                        this_res_lst[3] = f'{def_["ex"]["#text"]} '
                    else:
                        this_res_lst[3] = f'{def_["ex"]} '
                
                res_lst.append(this_res_lst)
            res_lst_all.append(res_lst)

        return res_lst_all

    def lucky(self, num=1) -> None:
        assert num <= self.len_items, f'Number of items is {self.len_items}, but you want {num}'
        # generate random number without repetition
        random_lst = []
        while len(random_lst) < num:
            random_num = randint(0, self.len_items-1)
            if random_num not in random_lst:
                random_lst.append(random_num)
        # search for keys at those random numbers
        for random_num in random_lst:
            k, v = self.items[random_num]
            key = k.decode()
            print(f'Key: {key}')
            self.search(key)