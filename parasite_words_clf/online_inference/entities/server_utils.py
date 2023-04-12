import re
import torch
from transformers import BertTokenizer, BertModel
from src.models import ParasiteWordsClfHead
from nltk import tokenize

# PATH_TO_PARASITE_WORDS_CLF_HEAD = '../models/short_classif.pt'


class WordClassifier:
    def __init__(self, meta_info):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', padding=True)
        self.bert = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.bert.eval()
        self.context_independent_bad_words = ['ну']

        self.clf_heads = {}
        for bad_word, meta_data in meta_info.items():
            clf_head = ParasiteWordsClfHead(768, 1)
            clf_head.load_state_dict(torch.load(meta_data["model_path"]))
            self.clf_heads[bad_word] = {}
            self.clf_heads[bad_word]['model'] = clf_head
            self.clf_heads[bad_word]['id'] = meta_data['parasite_word_id']

        print(self.clf_heads)

    #         self.bad_word_token_ids = [cur_bad_word_id,]

    def classify(self, text):
        sents = tokenize.sent_tokenize(text)
        parasite_word_indexes = []
        words_count = 0

        for sentence in sents:
            print("sentence: ", sentence)
            sentence = sentence.lower()
            words_in_sent = re.split('\W+', sentence)
            if words_in_sent[-1] == '':
                words_in_sent = words_in_sent[0:-1]

            tokenized_sent = self.tokenizer(sentence, truncation=True, return_tensors='pt', padding='max_length',
                                            max_length=512)

            with torch.no_grad():
                model_output = self.bert(**tokenized_sent)
                word_embeddings = model_output[0].squeeze()

                predictions = {}
                counters = {}

                for bad_word, meta_data in self.clf_heads.items():
                    indexes_with_parasite_ids = [index for (index, item) in
                                                 enumerate(tokenized_sent['input_ids'][0].tolist()) if
                                                 item == meta_data['id']]

                    if len(indexes_with_parasite_ids) == 0:
                        continue
                    filtered_embeddings = torch.index_select(word_embeddings, 0,
                                                             torch.tensor(indexes_with_parasite_ids))
                    predictions[bad_word] = meta_data['model'](filtered_embeddings)

                    predictions[bad_word] = predictions[bad_word].squeeze(1)
                    predictions[bad_word] = (predictions[bad_word] > 0.5).float().tolist()

                    counters[bad_word] = -1

                for idx, word in enumerate(words_in_sent):
                    if word in counters.keys():
                        counters[word] += 1
                        if predictions[word][counters[word]] >= 0.9:
                            parasite_word_indexes.append(words_count + idx)

                    elif word in self.context_independent_bad_words:
                        parasite_word_indexes.append(words_count + idx)

            words_count += len(words_in_sent)
            print("words_count: ", words_count, words_in_sent)

        return parasite_word_indexes
