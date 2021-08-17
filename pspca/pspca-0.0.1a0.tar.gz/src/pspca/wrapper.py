"""scikit-learn API wrapper for PSPCA."""
from .utils import normalize
from .utils import pspca
from .utils import transform


class PSPCA(object):
    """scikit-learn API wrapper for PSPCA."""

    def __init__(self, dimension):
        """Initialize the object with dimension to reduce to."""
        self.dimension = dimension

        self.w, self.v, self.A = None, None, None

    def fit(self, x):
        """Fit PSPCA to data in x."""
        self.w, self.v, self.A = pspca(x)

    def transform(self, x):
        """Transform data x in the PSPCA eigenvectors with fewer dimensions."""
        return self.full_transform(x)[:, : self.dimension]

    def fit_transform(self, x):
        """Run fit and transform on same data x."""
        self.fit(x)
        return self.transform(x)

    def full_transform(self, x):
        """Transform data x in the PSPCA eigenvectors."""
        return transform(normalize(x), self.v)
