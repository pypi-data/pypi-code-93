import numpy as np
from ndn4sid import linearalgebra
from ndn4sid import systems
from ndn4sid import misc


def test_get_hankel_tensor():
    data_size = (2,5,8)
    order = (2,3)
    # Calculate the expected size.
    expected_size = (data_size[0],) + tuple([sub for k,l in zip(data_size[1:],order) for sub in (k-l+1,l)])
    # Generate random data.
    y = np.random.randn(*data_size)
    # Compute the Hankel tensor.
    H = systems.get_hankel_tensor(y,order)
    # Check if the size matches.
    assert H.shape == expected_size
    # Loop over all elements.
    for index in misc.shape_to_iterator(H.shape):
        data_index = (index[0],) + tuple([k+l for k,l in zip(index[1::2],index[2::2])])
        assert data_index == misc.tensor_index_to_data_index(index)
        assert H[index] == y[data_index]
        