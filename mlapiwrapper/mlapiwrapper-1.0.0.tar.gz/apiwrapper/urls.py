class URLs:
    def __init__(self, response_format="json", ):
        self.format = response_format

        self.base_url = "http://13.251.45.210:80/"
        self.preprocess = 'preprocess'
        self.predictSentiment = 'predictSentiment'
        self.getAspect = 'extract_aspect_words'
        self.getOpinion = 'extract_opinion_units'
        self.getQualifer = "extract_qualifier"

    def base_url(self):
        return self.base_url

    def preprocess_url(self):
        return self.base_url + self.preprocess

    def predictSentiment_url(self):
        return self.base_url + self.predictSentiment

    def getAspect_url(self):
        return self.base_url + self.getAspect

    def getOpinion_url(self):
        return self.base_url + self.getOpinion

    def getQualifier_url(self):
        return self.base_url + self.getQualifer
