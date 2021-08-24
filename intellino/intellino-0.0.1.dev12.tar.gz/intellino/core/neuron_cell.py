
import numpy as np
from typing import List


class NeuronCells:
    """
    NeuronCell Container for simulate Intellino
    """

    def __init__(self,
                 number_of_neuron_cells: int = 100,
                 length_of_input_vector: int = 196,
                 measure="manhattan") -> None:

        """

        Args:
            number_of_neuron_cells (int): number of neuron cell.
                                          it's corresponding number of Neuron Cell in Intelino hardware
            length_of_input_vector (int): length of vector.
                                          Intellino Hardware has limitation of vector length.
                                          this arguments means limitation of vector length in Intellino Hardware
            measure (str): method of distance measure.
                           default method is "manhattan" in Intellino Hardware

        Returns:
            (None)
        """
        self.number_of_neuro_cells: int = number_of_neuron_cells
        self.length_of_input_vector: int = length_of_input_vector
        self.cells: List = [Cell(self.length_of_input_vector, measure) for _ in range(self.number_of_neuro_cells)]

    def __len__(self):
        return len(self.cells)

    def inference(self, vector: np.ndarray) -> np.ndarray:
        """
        inference(classify)

        Args:
            vector (np.ndarray): input vector array for classify

        Retunrs:
            (np.ndarray): vector array as prediction result
        """
        vector = self.padding(vector)

        distances = list()
        for cell in self.cells:
            if not cell.is_registry:
                print("Not valid cell")
                break

            distances.append(float(cell.calc_distance(vector)))

        min_distance = np.min(distances)
        closest_cell_idx = distances.index(min_distance)

        return self.cells[closest_cell_idx].target

    def train(self,vector: np.ndarray, target: int) -> bool:
        """
        Train. train vector register(transmitter) into cell with target(label)

        Args:
            vector  (np.ndarray): input vector for train
            target  (int): target(label) for classify

        Returns:
            (bool): train was successful or not
        """

        assert len(vector.shape) == 1, f"Vector dimension should be One. but dim is {vector.shape}"
        assert vector.shape[0] <= self.length_of_input_vector, \
            f"Length of vector should less than arguments( given: {self.length_of_input_vector} ). " \
                f"but length is {vector.shape}"

        vector = self.padding(vector)

        for idx in range(len(self.cells)):
            if not self.cells[idx].is_registry:
                self.cells[idx].registry(input_vector=vector, target=target)

                # Return True means that Intellino Cells can keep training
                return False

        # Return False means finished train
        return True

    def padding(self, vector: np.ndarray) -> np.ndarray:
        """
        adding vector elements until length of vector same with length of vector argument.
        when length of vector less than length_of_input_vector

        Args:
            vector  (np.ndarray): input vector

        Returns:
            (np.ndarray): vector, length of vector same with length parameter
        """

        shape = vector.shape
        len_of_vector = len(vector)
        redundancy = self.length_of_input_vector - len_of_vector
        if len(shape) > 1:
            raise RuntimeError("vector shape is multi dimension")

        if redundancy == 0:
            return vector

        zeros = np.zeros(redundancy)
        return np.append(vector, zeros)


class Cell:
    """
    Neuron Cell
    """

    def __init__(self,
                 length_of_input_vector: int,
                 measure: str = "manhattan"):
        """
        Args:
            length_of_input_vector (int): number of neuron cell.
                                          it's corresponding number of Neuron Cell in Intelino hardware
            measure (str): method of distance measure.
                           default method is "manhattan" in Intellino Hardware

        Returns:
            (None)
        """
        self._vector: np.ndarray = np.zeros((1, length_of_input_vector), dtype=np.float)
        self._measure: str = measure
        self.target: int = 0
        self.is_registry = False

    def registry(self, input_vector: np.ndarray, target: int):
        """
        Args:
            input_vector (np.ndarray): input vector for train
            target (int): target(label) for classify

        Returns:
            (None)
        """
        self._vector: np.ndarray = input_vector
        self.target: int = target
        self.is_registry = True

    def calc_distance(self, input_vector: np.ndarray) -> np.ndarray:
        """
        Calculate distance input vector between with registered vector in cell

        Args:
            input_vector (np.ndarray): input vector for inference

        Returns:
            (np.ndarray): distance input vector between with registered vector in cell
        """

        if self._measure == "manhattan":
            return self.manhattan_distance(input_vector)
        elif self._measure == "euclidean":
            return self.euclidean_distance(input_vector)
        else:
            raise RuntimeError("{} is not supported measure".format(self._measure))

    def manhattan_distance(self, input_vector: np.ndarray) -> np.ndarray:
        input_vector = input_vector.astype(np.int16)
        self._vector = self._vector.astype(np.int16)
        return np.sum(np.abs(self._vector - input_vector))

    def euclidean_distance(self, input_vector: np.ndarray) -> np.ndarray:
        input_vector = input_vector.astype(np.int16)
        self._vector = self._vector.astype(np.int16)
        return np.sqrt(np.sum(np.power(self._vector - input_vector, 2)))
