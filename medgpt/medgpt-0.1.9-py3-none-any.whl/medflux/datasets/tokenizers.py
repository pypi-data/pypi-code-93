import random
import torch

class SimpleMapTokenizer(object):
    r''' Not even really a tokenizer, will take a list of tokens and
    covert them to IDs

    Args:
        tkn2id
        pad_id
        max_len
        start_id:
            If set it will be prepended to each input example
    '''
    def __init__(self, tkn2id, pad_id, max_len=50, start_id=None, id2type=None, cdb=None):
        self.tkn2id = tkn2id
        self.pad_id = pad_id
        self.max_len = max_len
        self.start_id = start_id
        self.id2type = id2type
        self.cdb = cdb

        # Create id2tkn 
        self.id2tkn = {v:k for k,v in self.tkn2id.items()}


    def __call__(self, text, return_tensors=False):
        out = {'input_ids': [], 'attention_mask': []}

        out['input_ids'] = [self.start_id] + [self.tkn2id[tkn] for tkn in text.split(" ")]
        out['attention_mask'] = [1] * len(out['input_ids'])

        if return_tensors:
            out = {k:torch.tensor([v]) for k,v in out.items()}

        return out


    def decode(self, token_ids, get_names=True):
        tkns = self.convert_ids2tokens(token_ids, get_names=get_names)
        if type(tkns) != list:
            tkns = [tkns]
        return " ".join(tkns)


    def convert_ids2tokens(self, token_ids, get_names=True):
        if type(token_ids) == torch.Tensor:
            token_ids = token_ids.tolist()
        if type(token_ids) == list and type(token_ids[0]) == torch.Tensor:
            token_ids = [x.tolist() for x in token_ids]

        # Same as decode, but needed for compatibility with ecco
        out = []
        if type(token_ids) != list:
            out = [self.id2tkn[int(token_ids)]]
        else:
            # Convert tokens to IDs
            out = [self.id2tkn[int(id)] for id in token_ids]

        if self.cdb is not None and get_names:
            _out = []
            for tkn in out:
                _out.append(self.cdb.get_name(tkn))
                #_out.append(" | ")
            out = _out

        return out



    def tokens_to_ids(self, tokens):
        r''' This will skip tokens if they are not in the tkn2id dict
        '''
        out = [self.tkn2id[tkn] for tkn in tokens if tkn in self.tkn2id]
        if self.start_id is not None:
            out = [self.start_id] + out
        out = out[:self.max_len]

        return out


    def encode(self, examples):
        r''' Convert 'stream' in the examples from tokens to IDs, save as 'input_ids'. Use with HF datasets.map
        '''
        examples['input_ids'] = [self.tokens_to_ids(stream[:-1]) for stream in examples['stream']]

        return examples


    def augment(self, examples, n_augmentations=1, shuffle_prob=0.5, episode_delimiter='age'):
        r''' Augment the data and add random permutations of examples ontop of existing ones

        Args:
            n_augmentations: Number of augmentations to be done per example
        '''
        if self.id2type is None:
            raise Exception("Requires self.id2type to be set")

        for ind, ids in enumerate(list(examples['input_ids'])):
            for i in range(n_augmentations):
                new_sample = [self.tkn2id['<START>']]
                episode = []
                for id in ids:
                    if len(episode) > 0 and self.id2type[id] == episode_delimiter:
                        if shuffle_prob >= random.random(): random.shuffle(episode)
                        new_sample.extend(episode)

                        # Append also the age
                        new_sample.append(id)
                        # Reset episode
                        episode = []
                    elif id == self.tkn2id['<START>'] or id == self.tkn2id['<PAD>']:
                        # Skip start and pad 
                        pass
                    else:
                        episode.append(id)
                if shuffle_prob >= random.random(): random.shuffle(episode)
                new_sample.extend(episode)

                # Append the new sample to input_ids
                examples['input_ids'].append(new_sample)
                # Append the duplicated patient_id
                examples['patient_id'].append(examples['patient_id'][ind])

        return examples
