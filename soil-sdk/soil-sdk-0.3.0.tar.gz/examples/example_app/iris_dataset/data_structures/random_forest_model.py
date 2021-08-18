'''
    DataStructure to serialize a Keras Model
    It puts the network architecture as metadata and pickles the weights.
'''
import pickle
from soil.data_structures.data_structure import DataStructure


class RandomForestModel(DataStructure):
    ''' Data Structure for a Sklearn Model '''
    @staticmethod
    def unserialize(serialized, metadata):
        ''' Function to deserialize '''
        return RandomForestModel(pickle.loads(serialized), metadata)

    def serialize(self):
        ''' Function to serialize '''
        return pickle.dumps(self.data)

    def get_data(self, **_args):
        # pylint: disable=no-self-use
        ''' Placeholder function for the API call '''
        return {}  # self.data
