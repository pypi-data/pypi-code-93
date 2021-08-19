from abc import ABC, abstractmethod
import sys
from enum import Enum

class ModelConverter(ABC):
    def __init__(self, model=None):
        self.model = self.load_model(model) if isinstance(model, str) else model 
        self.source_format = None
        self.target_format = None

    @abstractmethod
    def load_model(self, path=None):    
        """
        Load the model from path and returns the model
        """

    @abstractmethod
    def convert(self, dataloader=None):
        """
        Converts the model to the specific output format
        """

    @abstractmethod
    def save(self, path=""):
        """
        Save the model to disk in a specific format
        """