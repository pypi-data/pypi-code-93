import unittest


class DataloaderUnitTest(unittest.TestCase):

    def _check_pair(self, x, y):
        #  data and labels must have equal lenth
        self.assertEqual(len(x), len(y))

        #  data and labels must have at least one sample
        self.assertTrue(len(x) > 0)

    def _check_train_test(self, xtrain, ytrain, xtest, ytest):
        #  at least two samples for training, at least one sample for testing
        self.assertTrue(len(xtrain) >= 2)
        self.assertTrue(len(xtest) >= 1)

        #  as many labels as training samples
        self.assertEqual(len(xtrain), len(ytrain))
        self.assertEqual(len(xtest), len(ytest))

        #  at least two distinctive classes
        self.assertTrue(len(set(ytrain)) > 1)

        #  every test class must be present for training
        self.assertTrue(set(ytrain) >= set(ytest))

    def _loader_sanity_check(self,
                             xtrain,
                             ytrain,
                             xval=None,
                             yval=None,
                             xtest=None,
                             ytest=None):
        self._check_pair(xtrain, ytrain)

        if xtest is not None:
            self.assertTrue(ytest is not None)
            self._check_pair(xtest, ytest)
            self._check_train_test(xtrain, ytrain, xtest, ytest)

        if xval is not None:
            self.assertTrue(yval is not None)
            self._check_pair(xval, yval)
            self._check_train_test(xtrain, ytrain, xval, yval)
