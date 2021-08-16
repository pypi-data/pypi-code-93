# import os
# from .data_helper import DataHelper
# from .normalizer import Normalizer
#
#
# class FindStems():
#
#     def __init__(self):
#
#         self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
#
#         self.noun_lex_path = self.dir_path + "resource/stemmer/stem_lex.pckl"
#         self.verb_lex_path = self.dir_path + "resource/stemmer/verbStemDict.pckl"
#         self.verb_tense_map_path = self.dir_path + "resource/stemmer/stem_verbMap.pckl"
#         self.irregular_nouns_path = self.dir_path + "resource/stemmer/stem_irregularNounDict.pckl"
#         self.prefix_list_path = self.dir_path + "resource/stemmer/pishvand.txt"
#         self.postfix_list_path = self.dir_path + "resource/stemmer/pasvand.txt"
#         self.verb_tense_file_path = self.dir_path + "resource/stemmer/verb_tense.txt"
#         self.mokasar_noun_path = self.dir_path + "resource/stemmer/mokasar.txt"
#         self.data_helper = DataHelper()
#
#         if (os.path.isfile(self.noun_lex_path) and os.path.isfile(self.verb_lex_path)
#                 and os.path.isfile(self.verb_tense_map_path) and os.path.isfile(self.irregular_nouns_path)):
#             self.noun_lexicon = self.data_helper.load_var(self.noun_lex_path)
#             self.verb_lexicon = self.data_helper.load_var(self.verb_lex_path)
#             self.verb_tense_map = self.data_helper.load_var(self.verb_tense_map_path)
#             self.irregular_nouns = self.data_helper.load_var(self.irregular_nouns_path)
#
#             self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]
#
#         else:
#             self.mynormalizer = Normalizer()
#             self.noun_lexicon, self.verb_lexicon, \
#             self.verb_tense_map, self.irregular_nouns = \
#                 self.data_helper.build_stem_dictionary(self.mynormalizer,
#                                                        self.verb_tense_file_path,
#                                                        self.mokasar_noun_path)
#             self.data_helper.save_var(save_path=self.noun_lex_path, variable=self.noun_lexicon)
#             self.data_helper.save_var(save_path=self.verb_lex_path, variable=self.verb_lexicon)
#             self.data_helper.save_var(save_path=self.verb_tense_map_path, variable=self.verb_tense_map)
#             self.data_helper.save_var(save_path=self.irregular_nouns_path, variable=self.irregular_nouns)
#
#             self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]
#
#         self.prefix_list = set({})
#         with open(self.prefix_list_path, "r", encoding='utf-8') as pishvand_input_file:
#             pishvandFile_content = pishvand_input_file.readlines()
#             for el in pishvandFile_content:
#                 self.prefix_list.add(el.strip())
#
#         self.postfix_list = set({})
#         with open(self.postfix_list_path, "r", encoding='utf-8') as pasvand_input_file:
#             pasvandFile_content = pasvand_input_file.readlines()
#             for el in pasvandFile_content:
#                 self.postfix_list.add(el.strip())
#
#     def select_candidate(self, candidate_list, lexicon_set=None):
#         length = 1000
#         selected = ""
#         for tmp_candidate in candidate_list:
#             if lexicon_set == None and len(tmp_candidate) < length:
#                 selected = tmp_candidate
#                 length = len(tmp_candidate)
#             elif (lexicon_set != None) and (tmp_candidate in lexicon_set):
#                 if (length == 1000):
#                     selected = tmp_candidate
#                     length = len(tmp_candidate)
#                 else:
#                     if (len(tmp_candidate) > length):
#                         selected = tmp_candidate
#                         length = len(tmp_candidate)
#         return selected
#
#     def is_prefix(self, word, prefix):
#         word = word.strip("\u200c")
#         return word.startswith(prefix)
#
#     def is_postfix(self, word, post):
#         word = word.strip("\u200c")
#         return word.endswith(post)
#
#     def remove_prefixes(self, word, prefix):
#         word = word.strip("\u200c")
#         candidateStem = set({})
#         last_el = ''
#         for el in prefix:
#             if word.startswith(el):
#                 if len(el) > 0:
#
#                     if len(el) > len(last_el):
#                         last_el = el
#                         tmp = word[len(el):].strip().strip('\u200c')
#                 else:
#                     tmp = word
#                 candidateStem.add(tmp)
#         return last_el, candidateStem
#
#     def remove_postfixes(self, word, postfix):
#
#         word = word.strip("\u200c")
#         candidateStem = set({})
#         last_el = ''
#         for el in postfix:
#
#             if word.endswith(el):
#                 if len(el) > 0:
#                     if len(el) > len(last_el):
#                         last_el = el
#                         tmp = word[:-len(el)].strip().strip('\u200c')
#                 else:
#                     tmp = word
#                 candidateStem.add(tmp)
#
#         return last_el, candidateStem
#
#     def map_irregular_noun(self, word):
#
#         if word in self.irregular_nouns:
#             return self.irregular_nouns[word]
#         else:
#
#             return word
#
#     def convert_to_stem(self, word, word_pos=None):
#         word = word.strip(" ")
#
#         if word in self.noun_lexicon:
#
#             if (word_pos == None or word_pos == 'N'):
#                 # print("in word dict...")
#                 # return self.map_irregular_noun(word)+' '
#                 return word
#
#
#         elif word in self.verb_lexicon:
#             if word_pos is None or word_pos == 'V':
#
#                 # print("in verb dict...")
#                 if word in self.verb_f2p_map:
#
#                     stem = self.verb_f2p_map[word] + "&" + word
#                 elif word in self.verb_p2f_map:
#
#                     stem = word + "&" + self.verb_p2f_map[word]
#
#                 else:
#                     stem = word
#                 return word
#
#
#         # if word is a verb
#         if word_pos is None or word_pos == "V":
#
#             # ماضی مستمر
#             prefix_tmp = []
#             postfix_tmp = []
#
#             prefix_word, candidate_list = self.remove_prefixes(word, ["داشتم", "داشتی", "داشت",
#                                                                       "داشتیم", "داشتید", "داشتند"])
#             prefix_tmp.append(prefix_word)
#             if len(candidate_list) > 0:
#
#                 new_word = self.select_candidate(candidate_list)
#                 prefix_word, candidate_list = self.remove_prefixes(new_word, ["می"])
#                 prefix_tmp.append(prefix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list)
#                     postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
#                                                                                     "م", "ی", ""])
#                     postfix_tmp.append(postfix_word)
#                     if len(candidate_list) > 0:
#                         new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                         if new_word:
#                             if new_word in self.verb_p2f_map:
#                                 stem = new_word + "&" + self.verb_p2f_map[new_word]
#                                 output = ''
#                                 for i in prefix_tmp:
#                                     output += i + "\u200c"
#                                 output += new_word
#                                 for i in postfix_tmp:
#                                     output += i
#
#                                 return output
#
#             # مضارع مستمر
#
#             prefix_tmp = []
#             postfix_tmp = []
#             prefix_word, candidate_list = self.remove_prefixes(word, ["دارم", "داری", "دارد",
#                                                                       "داریم", "دارید", "دارند"])
#             prefix_tmp.append(prefix_word)
#             if len(candidate_list) > 0:
#
#                 new_word = self.select_candidate(candidate_list)
#                 prefix_word, candidate_list = self.remove_prefixes(new_word, ["می"])
#                 prefix_tmp.append(prefix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list)
#                     postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
#                                                                                     "م", "ی", "د"])
#                     postfix_tmp.append(postfix_word)
#                     if len(candidate_list) > 0:
#                         new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                         if new_word:
#                             if new_word in self.verb_f2p_map:
#                                 stem = self.verb_f2p_map[new_word] + "&" + new_word
#
#                                 output = ''
#                                 for i in prefix_tmp:
#                                     output += i + "\u200c"
#                                 output += new_word
#                                 for i in postfix_tmp:
#                                     output += i
#
#                                 return output
#
#             # مضارع اخباری
#             prefix_tmp = []
#             postfix_tmp = []
#
#             prefix_word, candidate_list = self.remove_prefixes(word, ["می", "نمی", "همی"])
#             prefix_tmp.append(prefix_word)
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
#                                                                                 "م", "ی", "د"])
#                 postfix_tmp.append(postfix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                     if new_word:
#                         if new_word in self.verb_f2p_map:
#                             stem = self.verb_f2p_map[new_word] + "&" + new_word
#                             output = ''
#                             for i in prefix_tmp:
#                                 output += i + "\u200c"
#                             output += new_word
#                             for i in postfix_tmp:
#                                 output += i
#
#                             return output
#
#             # ماضی استمراری
#             prefix_tmp = []
#             postfix_tmp = []
#
#             prefix_word, candidate_list = self.remove_prefixes(word, ["می", "نمی", "همی"])
#             prefix_tmp.append(prefix_word)
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
#                                                                                 "م", "ی", ""])
#                 postfix_tmp.append(postfix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                     if new_word:
#                         if new_word in self.verb_p2f_map:
#                             stem = new_word + "&" + self.verb_p2f_map[new_word]
#                             output = ''
#                             for i in prefix_tmp:
#                                 output += i + "\u200c"
#                             output += new_word
#                             for i in postfix_tmp:
#                                 output += i
#
#                             return output
#
#             # ماضی بعید و التزامی
#             prefix_tmp = []
#             postfix_tmp = []
#
#             postfix_word, candidate_list = self.remove_postfixes(word, ["یم", "ید", "ند",
#                                                                         "م", "ی", ""])
#             postfix_tmp.append(postfix_word)
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["بود", "باشد", "باش"])
#                 postfix_tmp.append(postfix_word)
#
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list)
#                     postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
#                     postfix_tmp.append(postfix_word)
#                     if len(candidate_list) > 0:
#                         new_word = self.select_candidate(candidate_list)
#                         prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
#                         prefix_tmp.append(prefix_word)
#                         if len(candidate_list) > 0:
#                             new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                             if new_word:
#                                 if new_word in self.verb_p2f_map:
#                                     stem = new_word + "&" + self.verb_p2f_map[new_word]
#                                     output = ''
#                                     for i in prefix_tmp:
#                                         output += i
#                                     output += new_word
#                                     output += postfix_tmp[-1] + " "
#                                     output += postfix_tmp[-2]
#                                     output += postfix_tmp[-3]
#
#                                     return output
#
#             # ماضی نقلی
#             prefix_tmp = []
#             postfix_tmp = []
#             postfix_word, candidate_list = self.remove_postfixes(word, ["ام", "ای", "است",
#                                                                         "ایم", "اید", "اند"])
#             postfix_tmp.append(postfix_word)
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
#                 postfix_tmp.append(postfix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list)
#                     prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
#                     prefix_tmp.append(prefix_word)
#                     if len(candidate_list) > 0:
#                         new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                         if new_word:
#                             if new_word in self.verb_p2f_map:
#                                 stem = new_word + "&" + self.verb_p2f_map[new_word]
#                                 output = ''
#                                 for i in prefix_tmp:
#                                     output += i
#                                 output += new_word
#                                 for i in reversed(postfix_tmp):
#                                     output += i + "\u200c"
#
#                                 return output
#
#             # ماضی ابعد
#             prefix_tmp = []
#             postfix_tmp = []
#             postfix_word, candidate_list = self.remove_postfixes(word, ["ام", "ای", "است",
#                                                                         "ایم", "اید", "اند"])
#             postfix_tmp.append(postfix_word)
#
#             if len(candidate_list) > 0:
#
#                 new_word = self.select_candidate(candidate_list)
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
#                 postfix_tmp.append(postfix_word)
#                 if len(candidate_list) > 0:
#
#                     new_word = self.select_candidate(candidate_list)
#                     postfix_word, candidate_list = self.remove_postfixes(new_word, ["بود"])
#                     postfix_tmp.append(postfix_word)
#                     if len(candidate_list) > 0:
#
#                         new_word = self.select_candidate(candidate_list)
#                         postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
#                         postfix_tmp.append(postfix_word)
#                         if len(candidate_list) > 0:
#                             new_word = self.select_candidate(candidate_list)
#                             prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
#                             prefix_tmp.append(prefix_word)
#                             if len(candidate_list) > 0:
#
#                                 new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#
#                                 if new_word:
#
#                                     if new_word in self.verb_p2f_map:
#                                         stem = new_word + "&" + self.verb_p2f_map[new_word]
#                                         output = ''
#                                         for i in prefix_tmp:
#                                             output += i
#                                         output += new_word
#                                         output += postfix_tmp[-1]+"\u200c"
#                                         output += postfix_tmp[-2]
#                                         output += postfix_tmp[-3]+"\u200c"
#                                         output += postfix_tmp[-4]
#
#                                         return output
#
#             # آینده
#             prefix_tmp = []
#             postfix_tmp = []
#             prefix_word, candidate_list = self.remove_prefixes(word, ["خواه", "نخواه"])
#             prefix_tmp.append(prefix_word)
#
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#                 prefix_word, candidate_list = self.remove_prefixes(new_word, ["یم", "ید", "ند",
#                                                                               "م", "ی", "د"])
#                 prefix_tmp.append(prefix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                     if new_word:
#                         if new_word in self.verb_p2f_map:
#                             stem = new_word + "&" + self.verb_p2f_map[new_word]
#                             output = ''
#                             output += prefix_tmp[0]
#                             output += prefix_tmp[1] + "\u200c"
#                             output += new_word
#
#                             return output
#
#             # مضارع التزامی و امر
#             prefix_tmp = []
#             postfix_tmp = []
#             prefix_word, candidate_list = self.remove_prefixes(word, ["ب", "ن", ""])
#             prefix_tmp.append(prefix_word)
#             if len(candidate_list) > 0:
#
#                 new_word = self.select_candidate(candidate_list)
#                 postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند", "م",
#                                                                                 "ی", "د", ""])
#                 postfix_tmp.append(postfix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list)
#                     if (self.is_prefix(new_word, "یا")) and (new_word not in self.verb_lexicon):
#                         prefix_word, candidate_list = self.remove_prefixes(new_word, ["یا"])
#                         prefix_tmp.append(prefix_word)
#                         new_word = self.select_candidate(candidate_list)
#                         new_word = "آ" + new_word
#                     if self.is_postfix(new_word, "آی") or self.is_postfix(new_word, "ای"):
#                         if new_word not in self.verb_lexicon:
#                             postfix_word, candidate_list = self.remove_postfixes(new_word, ["ی"])
#                             postfix_tmp.append(postfix_word)
#                             new_word = self.select_candidate(candidate_list)
#                     if self.is_prefix(new_word, "ی"):
#                         prefix_word, candidate_list = self.remove_prefixes(new_word, ["ی"])
#                         prefix_tmp.append(prefix_word)
#                         tmp_word = self.select_candidate(candidate_list)
#                         if tmp_word and ("ا" + tmp_word) in self.verb_lexicon:
#                             new_word = "ا" + tmp_word
#
#                 if new_word and new_word in self.verb_lexicon:
#                     if new_word in self.verb_f2p_map:
#                         stem = self.verb_f2p_map[new_word] + "&" + new_word
#
#                         output = ''
#                         for i in prefix_tmp:
#                             output += i
#                         output += new_word + "\u200c"
#                         for i in reversed(postfix_tmp):
#                             output += i + "\u200c"
#
#                         return word
#
#             # ماضی ساده
#             prefix_tmp = []
#             postfix_tmp = []
#
#             postfix_word, candidate_list = self.remove_postfixes(word, ["م", "ی", "",
#                                                                         "یم", "ید", "ند"])
#             postfix_tmp.append(postfix_word)
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list)
#                 prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
#                 prefix_tmp.append(prefix_word)
#                 if len(candidate_list) > 0:
#                     new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                     if new_word:
#                         if new_word in self.verb_p2f_map:
#                             stem = new_word + "&" + self.verb_p2f_map[new_word]
#                             output = ''
#                             for i in prefix_tmp:
#                                 output += i + "\u200c"
#                             output += new_word + "\u200c"
#                             for i in postfix_tmp:
#                                 output += i + "\u200c"
#
#                             return word
#
#
#             # حالت مصدر
#             prefix_tmp = []
#             postfix_tmp = []
#             postfix_word, candidate_list = self.remove_postfixes(word, ["ن",""])
#             postfix_tmp.append(postfix_word)
#
#             if len(candidate_list) > 0:
#                 new_word = self.select_candidate(candidate_list, self.verb_lexicon)
#                 if new_word:
#
#                     if new_word in self.verb_p2f_map:
#                         stem = new_word + "&" + self.verb_p2f_map[new_word]
#                         output = ''
#                         output += new_word + "\u200c"
#                         for i in postfix_tmp:
#                             output += i + "\u200c"
#
#                         return word
#
#         if word in ["است"]:
#             return word
#
#         if word_pos is None or word_pos == "N":
#
#             stem_candidate = word
#             result_output = {}
#             postfix_tmp = []
#
#             prefix_tmp = []
#             prefix1, candidate_list = self.remove_prefixes(word, self.prefix_list)
#             prefix_tmp.append(prefix1)
#             prefix_tmp = list(filter(('').__ne__, prefix_tmp))
#
#             if len(candidate_list) > 0:
#
#                 stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
#                 if stem_candidate:
#                     new_word = stem_candidate
#                 else:
#                     new_word = self.select_candidate(candidate_list)
#                 stem_candidate = new_word
#             else:
#                 new_word = stem_candidate
#
#             if new_word in self.noun_lexicon:
#                 result_output['prefix'] = prefix_tmp[0]
#                 result_output['word'] = self.map_irregular_noun(new_word)
#
#                 return str(result_output['prefix']) + ' ' + str(result_output['word']) + ' '
#
#             stem_candidate = word
#             result_output = {}
#             postfix_tmp = []
#
#             # پسوندهای مالکیت
#             postfix, candidate_list = self.remove_postfixes(word, ["یم", "یت", "یش",
#                                                                    "یتان", "یشان", "یمان",
#                                                                    "مان", "تان", "شان", "ان", "ام", "م", "ت", "دان",
#                                                                    "ش"])
#             # add by aliebi to this list : ام خانه‌ام و دان نمکدان
#             postfix_tmp.append(postfix)
#             postfix_tmp = list(filter(('').__ne__, postfix_tmp))
#             if len(candidate_list) > 0:
#                 stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
#                 if stem_candidate:
#                     new_word = stem_candidate
#                 else:
#                     new_word = self.select_candidate(candidate_list)
#                 stem_candidate = new_word
#             else:
#                 new_word = stem_candidate
#             if new_word in self.noun_lexicon:
#                 text = ''
#                 text += self.map_irregular_noun(new_word) + ' '
#                 for i in reversed(postfix_tmp):
#                     text += i + ' '
#
#                 return text
#
#             postfix, candidate_list = self.remove_postfixes(new_word, ["ها", "ات", "های",
#                                                                        "ان", "هایی", "ین"])
#             postfix_tmp.append(postfix)
#             postfix_tmp = list(filter(('').__ne__, postfix_tmp))
#             if len(candidate_list) > 0:
#                 stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
#                 if stem_candidate:
#                     new_word = stem_candidate
#                 else:
#                     new_word = self.select_candidate(candidate_list)
#                 stem_candidate = new_word
#             else:
#                 new_word = stem_candidate
#
#             if new_word in self.noun_lexicon:
#
#                 text = ''
#                 text += self.map_irregular_noun(new_word) + ' '
#                 for i in reversed(postfix_tmp):
#                     text += i + ' '
#
#                 return text
#
#             postfix, candidate_list = self.remove_postfixes(new_word, self.postfix_list)
#             postfix_tmp.append(postfix)
#             postfix_tmp = list(filter(('').__ne__, postfix_tmp))
#             #
#             if len(candidate_list) > 0:
#                 stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
#                 if stem_candidate:
#                     new_word = stem_candidate
#                 else:
#                     new_word = self.select_candidate(candidate_list)
#                 stem_candidate = new_word
#             else:
#                 new_word = stem_candidate
#             if new_word in self.noun_lexicon:
#
#                 text = ''
#                 text += self.map_irregular_noun(new_word) + ' '
#                 for i in reversed(postfix_tmp):
#                     text += i + ' '
#
#                 return text
#
#                 # stem = new_word
#
#             # postfix,candidate_list = self.remove_postfixes(new_word, ["گ"])
#             # if len(candidate_list) > 0:
#             #     new_word = self.select_candidate(candidate_list)
#             #     new_word = new_word + "ه"
#             #     stem_candidate = new_word
#             # else:
#             #     new_word = stem_candidate
#             # if new_word in self.noun_lexicon:
#             #
#             #     result_output['prefix'] = []
#             #     result_output['word'] = self.map_irregular_noun(new_word)
#             #     result_output['postfix'] = postfix_tmp
#             #     return result_output
#
#             prefix_tmp = []
#             prefix1, candidate_list = self.remove_prefixes(new_word, self.prefix_list)
#             prefix_tmp.append(prefix1)
#             prefix_tmp = list(filter(('').__ne__, prefix_tmp))
#
#             if len(candidate_list) > 0:
#
#                 stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
#                 if stem_candidate:
#                     new_word = stem_candidate
#                 else:
#                     new_word = self.select_candidate(candidate_list)
#                 stem_candidate = new_word
#             else:
#                 new_word = stem_candidate
#
#             if new_word in self.noun_lexicon:
#
#                 text = str(prefix_tmp[0]) + ' '
#                 text += self.map_irregular_noun(new_word) + ' '
#                 for i in reversed(postfix_tmp):
#                     text += i + ' '
#
#                 return text
#
#                 # stem = new_word
#
#         # افعال پیشوندی
#         # candidate_list = self.remove_prefixes(word, ['در', 'بر', 'پر', 'باز',
#         #                                              'ور', 'فرو', 'فرا', 'وا'])
#         #
#         # if len(candidate_list) > 0:
#         #     new_word = self.select_candidate(candidate_list)
#         #     if new_word:
#         #         tmp_pr = word[:-len(new_word)].strip().strip('\u200c')
#         #         new_word = self.convert_to_stem(new_word, word_pos='V')
#         #         if new_word and new_word in self.verb_lexicon:
#         #             return tmp_pr + new_word
#
#
#         return word
import os
import re

from .data_helper import DataHelper
from .normalizer import Normalizer
import json


class FindStems():

    def __init__(self, config_file, double_postfix_joint):

        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

        self.noun_lex_path = self.dir_path + "resource/stemmer/stem_lex.pckl"
        self.mini_noun_lex_path = self.dir_path + "resource/stemmer/original_parsivar_stem_lex.pckl"
        self.verb_lex_path = self.dir_path + "resource/stemmer/verbStemDict.pckl"
        self.verb_tense_map_path = self.dir_path + "resource/stemmer/stem_verbMap.pckl"
        self.irregular_nouns_path = self.dir_path + "resource/stemmer/stem_irregularNounDict.pckl"
        self.prefix_list_path = self.dir_path + "resource/stemmer/pishvand.txt"
        self.postfix_list_path = self.dir_path + "resource/stemmer/pasvand.txt"
        self.verb_tense_file_path = self.dir_path + "resource/stemmer/verb_tense.txt"
        self.mokasar_noun_path = self.dir_path + "resource/stemmer/mokasar.txt"
        self.data_helper = DataHelper()

        if (os.path.isfile(self.noun_lex_path) and os.path.isfile(self.verb_lex_path)
                and os.path.isfile(self.verb_tense_map_path) and os.path.isfile(self.irregular_nouns_path)):
            self.noun_lexicon = self.data_helper.load_var(self.noun_lex_path)
            self.mini_lexicon = self.data_helper.load_var(self.mini_noun_lex_path)
            self.verb_lexicon = self.data_helper.load_var(self.verb_lex_path)
            self.verb_tense_map = self.data_helper.load_var(self.verb_tense_map_path)
            self.irregular_nouns = self.data_helper.load_var(self.irregular_nouns_path)

            self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]

        else:
            self.mynormalizer = Normalizer()
            self.noun_lexicon, self.verb_lexicon, \
            self.verb_tense_map, self.irregular_nouns, \
            self.mini_lexicon = \
                self.data_helper.build_stem_dictionary(self.mynormalizer,
                                                       self.verb_tense_file_path,
                                                       self.mokasar_noun_path)
            self.data_helper.save_var(save_path=self.noun_lex_path, variable=self.noun_lexicon)
            self.data_helper.save_var(save_path=self.verb_lex_path, variable=self.verb_lexicon)
            self.data_helper.save_var(save_path=self.verb_tense_map_path, variable=self.verb_tense_map)
            self.data_helper.save_var(save_path=self.irregular_nouns_path, variable=self.irregular_nouns)
            self.data_helper.save_var(save_path=self.mini_noun_lex_path, variable=self.mini_lexiconi)

            self.verb_p2f_map, self.verb_f2p_map = self.verb_tense_map[0], self.verb_tense_map[1]

        # self.prefix_list = set({})
        # with open(self.prefix_list_path, "r", encoding='utf-8') as pishvand_input_file:
        #     pishvandFile_content = pishvand_input_file.readlines()
        #     for el in pishvandFile_content:
        #         self.prefix_list.add(el.strip())
        #
        # self.postfix_list = set({})
        # with open(self.postfix_list_path, "r", encoding='utf-8') as pasvand_input_file:
        #     pasvandFile_content = pasvand_input_file.readlines()
        #     for el in pasvandFile_content:
        #         self.postfix_list.add(el.strip())

        with open(config_file) as f:
            self.affix_list = json.load(f)
        self.double_postfix_joint = double_postfix_joint

    def select_candidate(self, candidate_list, lexicon_set=None):
        length = 1000
        selected = ""
        for tmp_candidate in candidate_list:
            if lexicon_set == None and len(tmp_candidate) < length:
                selected = tmp_candidate
                length = len(tmp_candidate)
            elif (lexicon_set != None) and (tmp_candidate in lexicon_set):
                if (length == 1000):
                    selected = tmp_candidate
                    length = len(tmp_candidate)
                else:
                    if (len(tmp_candidate) > length):
                        selected = tmp_candidate
                        length = len(tmp_candidate)
        return selected

    def is_prefix(self, word, prefix):
        word = word.strip("\u200c")
        return word.startswith(prefix)

    def is_postfix(self, word, post):
        word = word.strip("\u200c")
        return word.endswith(post)

    def remove_prefixes(self, word, prefix):
        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in prefix:
            if word.startswith(el):
                if len(el) > 0:

                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[len(el):].strip().strip('\u200c')
                else:
                    tmp = word
                candidateStem.add(tmp)
        return last_el, candidateStem

    def remove_postfixes(self, word, postfix):

        word = word.strip("\u200c")
        candidateStem = set({})
        last_el = ''
        for el in postfix:

            if word.endswith(el):
                if len(el) > 0:
                    if len(el) > len(last_el):
                        last_el = el
                        tmp = word[:-len(el)].strip().strip('\u200c')
                        candidateStem = set({})
                        candidateStem.add(tmp)
                else:
                    tmp = word

        return last_el, candidateStem

    def map_irregular_noun(self, word):

        if word in self.irregular_nouns:
            return self.irregular_nouns[word]
        else:

            return word

    def prefix_finder(self, word):
        prefix_tmp = []
        stem_candidate = word
        prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["prefix_all"])

        prefix_tmp.append(prefix1)
        prefix_tmp = list(filter(('').__ne__, prefix_tmp))

        if len(candidate_list) > 0:

            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            if stem_candidate:
                new_word = stem_candidate
            else:
                new_word = self.select_candidate(candidate_list)
        else:

            new_word = stem_candidate

        if new_word in self.noun_lexicon and len(prefix_tmp) > 0:
            return str(prefix_tmp[0]), str(self.map_irregular_noun(new_word))
        else:
            return "", word

    def irregular_postfix(self, word):

        postfix_irregular = []
        postfix, candidate_list = self.remove_postfixes(word, self.affix_list["irregular_postfix_all"])

        postfix_irregular.append(postfix)
        postfix_irregular = list(filter(('').__ne__, postfix_irregular))
        #
        if word in candidate_list: candidate_list.remove(word)

        if len(candidate_list) > 0:
            stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
            if stem_candidate:
                new_word = stem_candidate
            else:
                new_word = self.select_candidate(candidate_list)
        else:

            new_word = word

        if new_word in self.noun_lexicon and len(postfix_irregular) > 0:

            return self.map_irregular_noun(new_word), postfix_irregular[0]
        else:
            return word, ""
        # stem = new_word

    def postfix_g(self, word):
        #
        postfix, candidate_list = self.remove_postfixes(word, ["گ"])
        if len(candidate_list) > 0:
            new_word = self.select_candidate(candidate_list)
            new_word = new_word + "ه"

            if new_word in self.noun_lexicon:
                new_word
                return new_word, "گ"
            else:
                return word, ""
        else:
            return word, ""

    def convert_to_stem(self, word, word_pos=None):
        word = word.strip(" ")

        if word in self.mini_lexicon:

            if (word_pos == None or word_pos == 'N'):
                return word


        elif word in self.verb_lexicon:
            if word_pos is None or word_pos == 'V':

                # print("in verb dict...")
                if word in self.verb_f2p_map:

                    stem = self.verb_f2p_map[word] + "&" + word
                elif word in self.verb_p2f_map:

                    stem = word + "&" + self.verb_p2f_map[word]

                else:
                    stem = word
                return word

        # if word is a verb
        if word_pos is None or word_pos == "V":

            # ماضی مستمر
            prefix_tmp = []
            postfix_tmp = []

            prefix_word, candidate_list = self.remove_prefixes(word, ["داشتم", "داشتی", "داشت",
                                                                      "داشتیم", "داشتید", "داشتند"])
            prefix_tmp.append(prefix_word)
            if len(candidate_list) > 0:

                new_word = self.select_candidate(candidate_list)
                prefix_word, candidate_list = self.remove_prefixes(new_word, ["می"])
                prefix_tmp.append(prefix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list)
                    postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
                                                                                    "م", "ی", ""])
                    postfix_tmp.append(postfix_word)
                    if len(candidate_list) > 0:
                        new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                        if new_word:
                            if new_word in self.verb_p2f_map:
                                stem = new_word + "&" + self.verb_p2f_map[new_word]
                                output = ''
                                for i in prefix_tmp:
                                    output += i + "\u200c"
                                output += new_word
                                for i in postfix_tmp:
                                    output += i

                                return output

            # مضارع مستمر

            prefix_tmp = []
            postfix_tmp = []
            prefix_word, candidate_list = self.remove_prefixes(word, ["دارم", "داری", "دارد",
                                                                      "داریم", "دارید", "دارند"])
            prefix_tmp.append(prefix_word)
            if len(candidate_list) > 0:

                new_word = self.select_candidate(candidate_list)
                prefix_word, candidate_list = self.remove_prefixes(new_word, ["می"])
                prefix_tmp.append(prefix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list)
                    postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
                                                                                    "م", "ی", "د"])
                    postfix_tmp.append(postfix_word)
                    if len(candidate_list) > 0:
                        new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                        if new_word:
                            if new_word in self.verb_f2p_map:
                                stem = self.verb_f2p_map[new_word] + "&" + new_word

                                output = ''
                                for i in prefix_tmp:
                                    output += i + "\u200c"
                                output += new_word
                                for i in postfix_tmp:
                                    output += i

                                return output

            # مضارع اخباری
            prefix_tmp = []
            postfix_tmp = []

            prefix_word, candidate_list = self.remove_prefixes(word, ["می", "نمی", "همی"])
            prefix_tmp.append(prefix_word)
            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
                                                                                "م", "ی", "د"])
                postfix_tmp.append(postfix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                    if new_word:
                        if new_word in self.verb_f2p_map:
                            stem = self.verb_f2p_map[new_word] + "&" + new_word
                            output = ''
                            for i in prefix_tmp:
                                output += i + "\u200c"
                            output += new_word
                            for i in postfix_tmp:
                                output += i

                            return output

            # ماضی استمراری
            prefix_tmp = []
            postfix_tmp = []

            prefix_word, candidate_list = self.remove_prefixes(word, ["می", "نمی", "همی"])
            prefix_tmp.append(prefix_word)
            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند",
                                                                                "م", "ی", "د"])
                postfix_tmp.append(postfix_word)
                if len(candidate_list) > 0:

                    new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                    if new_word:

                        if new_word in self.verb_p2f_map:
                            stem = new_word + "&" + self.verb_p2f_map[new_word]
                            output = ''
                            for i in prefix_tmp:
                                output += i + "\u200c"
                            output += new_word
                            for i in postfix_tmp:
                                output += i

                            return output

            # ماضی بعید و التزامی
            prefix_tmp = []
            postfix_tmp = []

            postfix_word, candidate_list = self.remove_postfixes(word, ["یم", "ید", "ند",
                                                                        "م", "ی", ""])
            postfix_tmp.append(postfix_word)
            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)

                postfix_word, candidate_list = self.remove_postfixes(new_word, ["بود", "باشد", "باش"])
                postfix_tmp.append(postfix_word)

                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list)
                    postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
                    postfix_tmp.append(postfix_word)
                    if len(candidate_list) > 0:
                        new_word = self.select_candidate(candidate_list)
                        prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
                        prefix_tmp.append(prefix_word)
                        if len(candidate_list) > 0:
                            new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                            if new_word:
                                if new_word in self.verb_p2f_map:
                                    stem = new_word + "&" + self.verb_p2f_map[new_word]
                                    output = ''
                                    for i in prefix_tmp:
                                        output += i
                                    output += new_word
                                    output += postfix_tmp[-1] + "\u200c"
                                    output += postfix_tmp[-2]
                                    output += postfix_tmp[-3]

                                    return output

            # ماضی نقلی
            prefix_tmp = []
            postfix_tmp = []
            postfix_word, candidate_list = self.remove_postfixes(word, ["ام", "ای", "است",
                                                                        "ایم", "اید", "اند"])
            postfix_tmp.append(postfix_word)
            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
                postfix_tmp.append(postfix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list)
                    prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
                    prefix_tmp.append(prefix_word)
                    if len(candidate_list) > 0:
                        new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                        if new_word:
                            if new_word in self.verb_p2f_map:
                                stem = new_word + "&" + self.verb_p2f_map[new_word]
                                output = ''
                                for i in prefix_tmp:
                                    output += i
                                output += new_word
                                for i in reversed(postfix_tmp):
                                    output += i + "\u200c"

                                return output

            # ماضی ابعد
            prefix_tmp = []
            postfix_tmp = []
            postfix_word, candidate_list = self.remove_postfixes(word, ["ام", "ای", "است",
                                                                        "ایم", "اید", "اند"])
            postfix_tmp.append(postfix_word)

            if len(candidate_list) > 0:

                new_word = self.select_candidate(candidate_list)
                postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
                postfix_tmp.append(postfix_word)
                if len(candidate_list) > 0:

                    new_word = self.select_candidate(candidate_list)
                    postfix_word, candidate_list = self.remove_postfixes(new_word, ["بود"])
                    postfix_tmp.append(postfix_word)
                    if len(candidate_list) > 0:

                        new_word = self.select_candidate(candidate_list)
                        postfix_word, candidate_list = self.remove_postfixes(new_word, ["ه"])
                        postfix_tmp.append(postfix_word)
                        if len(candidate_list) > 0:
                            new_word = self.select_candidate(candidate_list)
                            prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
                            prefix_tmp.append(prefix_word)
                            if len(candidate_list) > 0:

                                new_word = self.select_candidate(candidate_list, self.verb_lexicon)

                                if new_word:

                                    if new_word in self.verb_p2f_map:
                                        stem = new_word + "&" + self.verb_p2f_map[new_word]
                                        output = ''
                                        for i in prefix_tmp:
                                            output += i
                                        output += new_word
                                        output += postfix_tmp[-1] + "\u200c"
                                        output += postfix_tmp[-2]
                                        output += postfix_tmp[-3] + "\u200c"
                                        output += postfix_tmp[-4]

                                        return output

            # آینده
            prefix_tmp = []
            postfix_tmp = []
            prefix_word, candidate_list = self.remove_prefixes(word, ["خواه", "نخواه"])
            prefix_tmp.append(prefix_word)

            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                prefix_word, candidate_list = self.remove_prefixes(new_word, ["یم", "ید", "ند",
                                                                              "م", "ی", "د"])
                prefix_tmp.append(prefix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                    if new_word:
                        if new_word in self.verb_p2f_map:
                            stem = new_word + "&" + self.verb_p2f_map[new_word]
                            output = ''
                            output += prefix_tmp[0]
                            output += prefix_tmp[1] + "\u200c"
                            output += new_word

                            return output

            # مضارع التزامی و امر
            prefix_tmp = []
            postfix_tmp = []
            prefix_word, candidate_list = self.remove_prefixes(word, ["ب", "ن", ""])
            prefix_tmp.append(prefix_word)
            if len(candidate_list) > 0:

                new_word = self.select_candidate(candidate_list)
                postfix_word, candidate_list = self.remove_postfixes(new_word, ["یم", "ید", "ند", "م",
                                                                                "ی", "د", ""])
                postfix_tmp.append(postfix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list)
                    if (self.is_prefix(new_word, "یا")) and (new_word not in self.verb_lexicon):
                        prefix_word, candidate_list = self.remove_prefixes(new_word, ["یا"])
                        prefix_tmp.append(prefix_word)
                        new_word = self.select_candidate(candidate_list)
                        new_word = "آ" + new_word
                    if self.is_postfix(new_word, "آی") or self.is_postfix(new_word, "ای"):
                        if new_word not in self.verb_lexicon:
                            postfix_word, candidate_list = self.remove_postfixes(new_word, ["ی"])
                            postfix_tmp.append(postfix_word)
                            new_word = self.select_candidate(candidate_list)
                    if self.is_prefix(new_word, "ی"):
                        prefix_word, candidate_list = self.remove_prefixes(new_word, ["ی"])
                        prefix_tmp.append(prefix_word)
                        tmp_word = self.select_candidate(candidate_list)
                        if tmp_word and ("ا" + tmp_word) in self.verb_lexicon:
                            new_word = "ا" + tmp_word

                if new_word and new_word in self.verb_lexicon:
                    if new_word in self.verb_f2p_map:
                        stem = self.verb_f2p_map[new_word] + "&" + new_word

                        output = ''
                        for i in prefix_tmp:
                            output += i
                        output += new_word + "\u200c"
                        for i in reversed(postfix_tmp):
                            output += i + "\u200c"

                        return word

            # ماضی ساده
            prefix_tmp = []
            postfix_tmp = []

            postfix_word, candidate_list = self.remove_postfixes(word, ["م", "ی", "",
                                                                        "یم", "ید", "ند"])
            postfix_tmp.append(postfix_word)
            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                prefix_word, candidate_list = self.remove_prefixes(new_word, ["ن", ""])
                prefix_tmp.append(prefix_word)
                if len(candidate_list) > 0:
                    new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                    if new_word:
                        if new_word in self.verb_p2f_map:
                            stem = new_word + "&" + self.verb_p2f_map[new_word]
                            output = ''
                            for i in prefix_tmp:
                                output += i + "\u200c"
                            output += new_word + "\u200c"
                            for i in postfix_tmp:
                                output += i + "\u200c"

                            return word

            # حالت مصدر
            prefix_tmp = []
            postfix_tmp = []
            postfix_word, candidate_list = self.remove_postfixes(word, ["ن", ""])
            postfix_tmp.append(postfix_word)

            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list, self.verb_lexicon)
                if new_word:

                    if new_word in self.verb_p2f_map:
                        stem = new_word + "&" + self.verb_p2f_map[new_word]
                        output = ''
                        output += new_word + "\u200c"
                        for i in postfix_tmp:
                            output += i + "\u200c"

                        return word

        if word in ["است"]:
            return word
        if word_pos is None or word_pos == "N":

            stem_candidate = word
            result_output = {}
            postfix_tmp = []
            # پسوندهای مالکیت

            postfix, candidate_list = self.remove_postfixes(word, self.affix_list["prop_postfix_all"])

            postfix_tmp.append(postfix)
            postfix_tmp = list(filter(('').__ne__, postfix_tmp))
            if len(candidate_list) > 0:
                stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
                if stem_candidate:
                    new_word = stem_candidate
                else:
                    new_word = self.select_candidate(candidate_list)
                stem_candidate = new_word
            else:
                new_word = stem_candidate

            # if new_word in self.noun_lexicon:
            #     text = ''
            #     text += self.map_irregular_noun(new_word)
            #     for i in reversed(postfix_tmp):
            #         if i in ["یم", "یت", "یش", "ش", "م", "ت"]:
            #             text += i
            #         else:
            #             text += ' ' + i
            #
            #     return text + ' '

            postfix, candidate_list = self.remove_postfixes(new_word, self.affix_list["plural_postfix_all"])
            postfix_tmp.append(postfix)
            postfix_tmp = list(filter(('').__ne__, postfix_tmp))
            if len(candidate_list) > 0:
                stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
                if stem_candidate:
                    new_word = stem_candidate
                else:
                    new_word = self.select_candidate(candidate_list)
                stem_candidate = new_word
            else:
                new_word = stem_candidate
            pre, new_word = self.prefix_finder(new_word)
            new_word, pos = self.irregular_postfix(new_word)
            new_word, ge = self.postfix_g(new_word)
            pos = ge + pos

            if new_word in self.noun_lexicon and word != new_word:

                if pre != "":
                    if pre in self.affix_list["prefix_joint"]:
                        text = pre
                    else:
                        text = pre + "\u200c"
                else:
                    text = ""
                text += self.map_irregular_noun(new_word)
                if pos in self.affix_list["postfix_joint"] + self.affix_list["irregular_postfix_joint"]:
                    text += pos
                elif pos != "":
                    text = text + "\u200c" + pos
                for i in reversed(postfix_tmp):
                    if self.double_postfix_joint and len(postfix_tmp) == 2 and postfix_tmp[1] in self.affix_list[
                        "plural_postfix_all"] and \
                            postfix_tmp[0] in self.affix_list["prop_postfix_all"]:
                        if postfix_tmp[1] in self.affix_list["postfix_joint"]:
                            text += postfix_tmp[1] + "\u200c" + postfix_tmp[0]
                        else:
                            text += '\u200c' + postfix_tmp[1] + "\u200c" + postfix_tmp[0]

                        break
                    if i in self.affix_list["postfix_joint"] + self.affix_list["irregular_postfix_joint"]:
                        text += i
                    else:
                        text += '\u200c' + i

                return text + '\u200c'
            #

            new_word, pos = self.irregular_postfix(word)

            if new_word in self.noun_lexicon:
                text = ''
                if pos in self.affix_list["postfix_joint"] + self.affix_list["irregular_postfix_joint"]:
                    text += self.map_irregular_noun(new_word)  + pos
                else:
                    text += self.map_irregular_noun(new_word) + '\u200c' + pos
                return text

            postfix, candidate_list = self.remove_postfixes(new_word, ["گ"])

            if len(candidate_list) > 0:
                new_word = self.select_candidate(candidate_list)
                new_word = new_word + "ه"
                stem_candidate = new_word

                if new_word in self.noun_lexicon:

                    if postfix in self.affix_list["postfix_joint"] + self.affix_list["irregular_postfix_joint"]:
                        return self.map_irregular_noun(new_word) + postfix_tmp
                    else:
                        return self.map_irregular_noun(new_word) + " " + postfix_tmp

            else:
                new_word = stem_candidate

            prefix_tmp = []
            prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["prefix_all"])
            prefix_tmp.append(prefix1)
            prefix_tmp = list(filter(('').__ne__, prefix_tmp))

            if len(candidate_list) > 0:

                stem_candidate = self.select_candidate(candidate_list, self.noun_lexicon)
                if stem_candidate:
                    new_word = stem_candidate
                else:
                    new_word = self.select_candidate(candidate_list)
                stem_candidate = new_word
            else:
                new_word = stem_candidate

            if new_word in self.noun_lexicon and len(prefix_tmp) != 0:
                if prefix_tmp[0] in self.affix_list["prefix_joint"] :
                    text = str(prefix_tmp[0])
                else:
                    text = str(prefix_tmp[0]) + '\u200c'

                text += self.map_irregular_noun(new_word)
                for i in reversed(postfix_tmp):
                    if i in self.affix_list["postfix_joint"] + self.affix_list["irregular_postfix_joint"]:
                        text +=i
                    else:
                        text =  text + '\u200c'

                return text

                stem = new_word

        # افعال پیشوندی
        prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["verb_prefix"])

        if len(candidate_list) > 0:
            new_word = self.select_candidate(candidate_list)
            if new_word:
                tmp_pr = word[:-len(new_word)].strip().strip('\u200c')
                # new_word = self.convert_to_stem(new_word, word_pos='V')
                if new_word and new_word in self.verb_lexicon:
                    if prefix1 in self.affix_list["verb_prefix_joint"]:
                        return prefix1 + new_word
                    else:
                        return prefix1 + '\u200c' + new_word

        # split  "می/نمی" from start of  all words
        # prefix1, candidate_list = self.remove_prefixes(word, self.affix_list["slang_verbs_prefix"])
        # print(candidate_list)
        # if len(candidate_list) > 0:
        #     new_word = self.select_candidate(candidate_list)
        #     if new_word:
        #         if new_word and new_word in self.noun_lexicon:
        #
        #                 return prefix1 + '\u200c' + new_word

        return word
