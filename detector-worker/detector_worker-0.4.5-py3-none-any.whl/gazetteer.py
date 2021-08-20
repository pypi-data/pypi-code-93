import spacy


class GazetteerTermExtractor:
    def __init__(self, term_list, tokenize=None, tokenize_spans=None):
        if tokenize is None:
            spacy_model = "en_core_web_sm"
            if not spacy.util.is_package(spacy_model):
                spacy.cli.download(spacy_model)
            self.en_model = spacy.load(spacy_model, disable=['ner', 'tagger', 'parser'])
            self.tokenize = self._spacy_tokenize
            self.tokenize_spans = self._spacy_tokenize_spans
        else:
            self.tokenize = tokenize
            self.tokenize_spans = tokenize_spans

        self.terms_by_lengths = {}
        for term in term_list:
            term = tuple(self.tokenize(term))
            length = len(term)
            if length not in self.terms_by_lengths:
                self.terms_by_lengths[length] = set()
            self.terms_by_lengths[length].add(term)
        self.window_sizes = sorted(list(self.terms_by_lengths.keys()))

    def extract_terms(self, text: str):
        sentence = self.tokenize_spans(text)
        tokens = [text[s:e] for s, e in sentence]

        found_terms = self._find_terms(tokens)
        unique_dnts = self._resolve_overlappings(found_terms, len(tokens))

        result = []
        for start, end in unique_dnts:
            start_char, end_char = sentence[start][0], sentence[end - 1][1]
            result.append((start_char, end_char))
        return result

    def _find_terms(self, tokens):
        found_terms = []
        n_tokens = len(tokens)
        for window_size in self.window_sizes:
            dnt_list = self.terms_by_lengths[window_size]
            for i in range(n_tokens - window_size + 1):
                window = tuple(tokens[i:i+window_size])
                if window in dnt_list:
                    found_terms.append((i, i+window_size))
        return found_terms

    @staticmethod
    def _resolve_overlappings(found_terms, n_tokens):
        unique_terms = []
        tok_id = 0
        while tok_id < n_tokens:
            overlapping_dnts = [(s, e) for s, e in found_terms if s <= tok_id < e]
            if len(overlapping_dnts) == 0:
                tok_id += 1
                continue

            end = max(e for s, e in overlapping_dnts)
            overlapping_dnts.extend((s, e) for s, e in found_terms if tok_id < s < end)
            start = tok_id
            end = max(e for s, e in overlapping_dnts)
            unique_terms.append((start, end))
            tok_id = end

        unique_terms = sorted(list(set(unique_terms)), key=lambda d: d[0])
        return unique_terms

    def _spacy_tokenize(self, text):
        tokens = self.en_model(text)
        return [str(t) for t in tokens]

    def _spacy_tokenize_spans(self, text):
        tokens = self.en_model(text)
        return [(t.idx, t.idx + len(str(t))) for t in tokens if len(str(t).strip()) > 0]


def test():
    extractor = GazetteerTermExtractor([
        "Azure", "Microsoft", "AI for LOC", "Power BI", "Xbox", "Xbox 360", "Xbox One X", "Xbox Series X", "AppSource", "SharePoint", "Azure DevOps"
    ])

    for text, terms in [
        ("I don't know how to use Azure", ["Azure"]),
        ("Microsoft is my favourite OS", ["Microsoft"]),
        ("I am working on new project called AI  for LOC", ["AI  for LOC"]),
        ("Power BI directional graph", ["Power BI"]),
        ("Xbox 360 is better than Xbox One, but worse than Xbox Series X!", ["Xbox 360", "Xbox", "Xbox Series X"]),
        ("I love App Source", []),
        ("SharePoint scenarios overview", ["SharePoint"]),
        ("Azure DevOps project must be used to store and manage​ your test cases, test plans, and test case results.", ["Azure DevOps"])
    ]:
        extracted_terms = [text[s:e] for s, e in extractor.extract_terms(text)]
        if terms != extracted_terms:
            print(text)
            print("Expected terms: %s" % terms)
            print("Actual terms: %s" % extracted_terms)
            print()


if __name__ == "__main__":
    test()