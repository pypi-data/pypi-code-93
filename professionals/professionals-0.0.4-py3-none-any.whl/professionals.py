import esam
import eons

######## START CONTENT ########

class Entity(esam.Datum):
    def __init__(self, id=0, name=eons.INVALID_NAME()):
        super().__init__(name)
        self.uniqueId = id
        self.image_url = ""
        self.contact_url = ""
        self.description = ""
        self.activities = []
        self.interests = []
        self.solicitations = []
        self.relationships = {}
