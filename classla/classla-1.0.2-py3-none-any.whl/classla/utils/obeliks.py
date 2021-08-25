"""
Utilities related to using reldi in the pipeline.
"""
import re

from obeliks.rules import tokenize
from obeliks.tokenizer import normalize, preprocess_tokens, index_of



def check_reldi():
    """
    Import necessary components from reldi to perform tokenization.
    """
    try:
        import classla
    except ImportError:
        raise ImportError(
            "Reldi is used but not present on your machine. Make sure you run 'git submodule init' and 'git submodule update' commands."
        )
    return True


class ObeliksTrainer():
    def __init__(self, lang='sl', type='standard', annotate_pos=False):
        """ Construct a reldi-based tokenizer by loading the reldi pipeline.
        """
        if lang not in ['sl', 'hr', 'sr', 'bg', 'mk']:
            raise Exception("Reldi tokenizer is currently only allowed in Slovene, Croatian and Serbian pipelines.")

        check_reldi()
        from classla.submodules.reldi_tokeniser import tokeniser
        self.nlp = tokeniser
        self.lang = lang
        self.type = type

        self.annotate_pos = annotate_pos

    def process_conllu(self, para, np):
        doc = []
        metadoc = []

        if para.startswith(u"\uFEFF"):
            para = para[1:]

        para_concat = ''.join(para)

        tokens = tokenize(para)

        metadata = '# newpar id = {}\n'.format(np)

        org_text = preprocess_tokens(tokens)

        token_regex = re.compile(r'<S/>|</?s>|<([wc])>([^<]+)</[wc]>')
        idx = 0
        ns = 1
        nt = 0
        old_ns = 1
        doc_sent = []
        for match in token_regex.finditer(tokens):
            val = match.group()
            if val == '<s>':
                nt = 0
                if ns != old_ns:
                    old_ns = ns
                metadata += '# sent_id = {}.{}\n'.format(np, ns)
                metadata += '# text = {}\n'.format(org_text[ns - 1])
            elif val == '</s>':
                metadoc.append(metadata)
                doc.append(doc_sent)
                doc_sent = []
                metadata = ''
                ns += 1
            elif val == '<S/>':
                pass
            else:
                tok = {}
                val = match.group(2)
                actual_val = ['']
                idx_of_token = index_of(para, val, idx, actual_val)
                if idx_of_token == -1:
                    print('Warning: Cannot compute token index. Token: "{}" Text: "{}"'.format(val, para))
                idx = max(idx, idx_of_token + len(actual_val[0]))
                idx_of_token += 1
                nt += 1
                tok['id'] = tuple([nt])
                tok['text'] = actual_val[0]
                if match.group(1) == 'c' and self.annotate_pos:
                    tok['upos'] = 'PUNCT'
                    tok['xpos'] = 'Z'
                if idx < len(para) and not para_concat[idx].isspace():
                    tok['misc'] = 'SpaceAfter=No'
                doc_sent.append(tok)

        return doc, metadoc

    def process_text(self, text, tei_root, pass_newdoc_id):
        np = 0
        doc = []
        metadoc = []
        for line in text:
            if line.isspace() or line == '':
                continue

            # Normalize exotic characters
            line = normalize(line)

            if pass_newdoc_id and line.startswith('# newdoc id = '):
                np = 0
            np += 1
            new_doc, new_metadoc = self.process_conllu(line, np)
            doc += new_doc
            metadoc += new_metadoc

        return doc, metadoc
    def run(self, text=None, pass_newdoc_id=False):
        text = text.splitlines()

        return self.process_text(text, None, pass_newdoc_id)

    def tokenize(self, document):
        """ Tokenize a document with the obeliks tokenizer and add results to appropriate format.
        """
        raw_text = '\n'.join(document) if isinstance(document, list) else document
        document, metadocument = self.run(text=raw_text)

        return raw_text, document, metadocument
