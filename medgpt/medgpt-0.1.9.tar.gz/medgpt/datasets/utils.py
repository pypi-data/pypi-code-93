import logging
import numpy as np
from medcat.utils.matutils import unitvec


def add_to_stream(examples, pt2tkn, last=False, prefix=None, unk_tkn='unk'):
    r''' Add information to the patient stream based on patient_id.

    Args:
        examples
        pt2tkn
        last
        unk_tkn:
            What token will be added if the patient_id is not in pt2tkn
    '''

    for i in range(len(examples['stream'])):
        to_append = [pt2tkn.get(examples['patient_id'][i], unk_tkn)]
        if prefix is not None:
            to_append = [prefix] + to_append

        if last:
            # Append as last token
            examples['stream'][i] = examples['stream'][i] + to_append
        else:
            examples['stream'][i] = to_append + examples['stream'][i]

    return examples


def remove_parents_from_stream(examples, ch2parents):
    for i in range(len(examples['stream'])):
        stream = examples['stream'][i]
        parents = set()
        new_stream = []

        for tkn in stream:
            if tkn in ch2parents:
                # Add only if not in parents
                if tkn not in parents:
                    new_stream.append(tkn)
                # Update parents
                parents.update(ch2parents[tkn])
            else:
                new_stream.append(tkn)

        examples['stream'][i] = new_stream

    return examples

def get_embeddings_for_tokens(dataset, cdb, context_type='medium', special_tokens=['<PAD>', '<START>'], normalize=True, tkn2type={}):
    r''' Given a stream of tokens get the embeddings from MedCAT and make the required maps.

    Args:
        dataset
        cdb
        context_type
        special_tokens
        normalize:
            If True the embedding vectors will be normalized
        tkn2type:
            Dictionary mapping from token to type
    Returns:
        embeddings
        tkn2id
        id2tkn
        id2type
        id2type_detailed
    '''
    embeddings = []
    tkn2id = {}
    id2tkn = {}
    id2type = {} # Is the token a CUI/Age/whatever
    id2type_detailed = {} # Will have cdb type_ids for CUIs and same as id2type for rest

    for tkns in dataset['stream']:
        for tkn in tkns:
            tkn = str(tkn)
            if tkn not in tkn2id:
                token_type = tkn2type.get(tkn, 'unk')
                token_type_detailed = token_type

                if tkn in cdb.cui2context_vectors and context_type in cdb.cui2context_vectors[tkn]:
                    vec = cdb.cui2context_vectors[tkn][context_type]

                    # Take the first type_id (should always be the most important one if there are more)
                    token_type_detailed = list(cdb.cui2type_ids.get(tkn, ['unk']))[0]
                elif token_type in {'age', 'sex', 'ethnicity'}:
                    # Token vector is randomly assigned
                    vec = np.random.rand(300)
                else:
                    # Just in case
                    logging.debug("Token type is unknown: " + tkn)
                    vec = np.random.rand(300)

                id2tkn[len(embeddings)] = tkn
                id2type[len(embeddings)] = token_type
                id2type_detailed = token_type_detailed
                tkn2id[tkn] = len(embeddings)

                vec = unitvec(vec) if normalize else vec
                embeddings.append(vec)

    # Add special tokens
    for tkn in special_tokens:
        token_type = 'special'

        id2tkn[len(embeddings)] = tkn
        id2type[len(embeddings)] = token_type
        tkn2id[tkn] = len(embeddings)
        if tkn != '<PAD>':
            embeddings.append(np.random.rand(len(embeddings[0])))
        else:
            embeddings.append(np.zeros(len(embeddings[0])))

    return embeddings, tkn2id, id2tkn, id2type, id2type_detailed


def stream_to_separate_examples(examples):
    r''' Convert a stream to separate examples that can be used to train
    a next concept predictor unable to handle sequences. Use with HF datasets map function.

    '''
    out = {}
    out['input_ids'] = [example[0:i+1] for example in examples['input_ids'] for i in range(len(example) - 1)]
    out['labels'] = [example[i+1] for example in examples['input_ids'] for i in range(len(example) - 1)]
    out['labels_all'] = [example[i+1:] for example in examples['input_ids'] for i in range(len(example) - 1)]
    out['patient_id'] = [id for ind, id in enumerate(examples['patient_id']) for _ in range(len(examples['input_ids'][ind]) - 1)]

    return out
