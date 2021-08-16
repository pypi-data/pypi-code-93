import torch

"""
📁 Image Classification Collator
"""
class ImageClassificationCollator:
    
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor
 
    def __call__(self, batch):
        encodings = self.feature_extractor([x["image"] for x in batch], return_tensors='pt')
        encodings['labels'] = torch.tensor([x["label"] for x in batch], dtype=torch.long)
        return encodings
