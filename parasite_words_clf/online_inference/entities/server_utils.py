import re
import torch
from transformers import BertTokenizer, BertModel
from src.models import ParasiteWordsClfHead

# PATH_TO_PARASITE_WORDS_CLF_HEAD = '../models/short_classif.pt'


class WordClassifier:
    def __init__(self, path_to_model):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', padding=True)
        self.bert = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.classif_head = ParasiteWordsClfHead(768, 1)
        self.classif_head.load_state_dict(torch.load(path_to_model))
        self.bert.eval()
        self.bad_word_token_ids = [80062, ]

    def classify(self, sentence) -> list:
        words_in_sent = re.split('\W+', sentence)
        tokenized_sent = self.tokenizer(sentence, truncation=True, return_tensors='pt', padding='max_length',
                                        max_length=512)

        indexes_with_bad_words = []
        indexes_with_bad_words = [index for (index, item) in enumerate(tokenized_sent['input_ids'][0].tolist()) if
                                  item == self.bad_word_token_ids[0]]

        if len(indexes_with_bad_words) == 0:
            return []
        with torch.no_grad():
            model_output = self.bert(**tokenized_sent)
            word_embeddings = model_output[0].squeeze()
            filtered_embeddings = torch.index_select(word_embeddings, 0, torch.tensor(indexes_with_bad_words))
            pred = self.classif_head(filtered_embeddings)
            pred = pred.squeeze(1)
            pred = (pred > 0.5).float().tolist()

            ans = []

            counters = {
                "короче": -1,
            }
            for idx, word in enumerate(words_in_sent):
                if word == 'короче':
                    counters[word] += 1
                    if counters[word] < len(pred) and pred[counters[word]] >= 0.9:
                        ans.append(idx)

            return ans

