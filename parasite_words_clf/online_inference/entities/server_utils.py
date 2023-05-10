import re
import torch
import logging
import nltk
import string
from time import process_time
from transformers import BertTokenizer, BertModel
from src.models import ParasiteWordsClfHead
from src.app_logger import get_logger
from datetime import datetime


class WordClassifier:
    def __init__(self, meta_info, device='cpu'):
        self.tokenizer = BertTokenizer.from_pretrained(
            'bert-base-multilingual-cased', padding=True)
        self.bert = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.bert.eval()
        self.context_independent_bad_words = ['ну', 'блин']

        self.clf_heads = {}
        for bad_word, meta_data in meta_info.items():
            clf_head = ParasiteWordsClfHead(768, 1)
            clf_head.load_state_dict(torch.load(meta_data["model_path"]))
            self.clf_heads[bad_word] = {}
            self.clf_heads[bad_word]['model'] = clf_head
            self.clf_heads[bad_word]['id'] = meta_data['parasite_word_id']

        self.logger = get_logger(type(self).__name__)
        self.device = device
        self.to(device)
        self.logger.info(f'clf heads: {self.clf_heads}')

    def predict(self, text:str):
        self.logger.info(f"Input text: {text}")
        if text is None:
            return []
        process_time_start = process_time()
        datetime_start = datetime.now()
        sents = nltk.tokenize.sent_tokenize(text)
        parasite_word_indexes = []
        words_count = 0

        for sentence in sents:
            sentence = sentence.lower()
            self.logger.info(f"Sentence: {sentence}")
            words_in_sent = nltk.word_tokenize(sentence)
            words_in_sent = [word for word in words_in_sent if (word not in string.punctuation and word != '...')]

            self.logger.info(f"Splitted words: {words_in_sent} ")

            tokenized_sent = self.tokenizer(sentence,
                                            truncation=True, return_tensors='pt',
                                            padding='max_length', max_length=512)

            tokenized_sent.to(self.device)

            with torch.no_grad():
                word_embeddings = torch.tensor([])
                predictions = {}
                counters = {}
                bw_to_inds_with_parasite_ids = {}
                empty_sentence = True

                for bad_word, meta_data in self.clf_heads.items():

                    bw_to_inds_with_parasite_ids[bad_word] = [
                        index for (index, item) in
                        enumerate(tokenized_sent['input_ids'][0].tolist()) if
                        item == meta_data['id']
                    ]
                    if len(bw_to_inds_with_parasite_ids[bad_word]) > 0:
                        empty_sentence = False

                if not empty_sentence:
                    model_output = self.bert(**tokenized_sent)
                    word_embeddings = model_output[0].squeeze()
                    print(type(word_embeddings))

                for bad_word, indexes_with_parasite_ids in bw_to_inds_with_parasite_ids.items():
                    model = self.clf_heads[bad_word]['model']

                    if len(indexes_with_parasite_ids) == 0:
                        continue

                    filtered_embeddings = torch.index_select(
                        word_embeddings, 0,
                        torch.tensor(indexes_with_parasite_ids).to(self.device)
                    )

                    predictions[bad_word] = model(filtered_embeddings)

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

        self.logger.info(f"Parasite words indexes: {parasite_word_indexes}")
        self.logger.info(f'Time of processing:\n'
                         f'process_time: {process_time() - process_time_start} seconds\n'
                         f'datetime: {datetime.now() - datetime_start} seconds')
        return parasite_word_indexes

    def to(self, device: str):
        self.device = device
        self.bert.to(device)
        for bad_word in self.clf_heads:
            self.clf_heads[bad_word]['model'].to(device)
        self.logger.info(f'Model set to {device}')
