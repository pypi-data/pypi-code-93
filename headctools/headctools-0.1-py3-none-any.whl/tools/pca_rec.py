import os

import SimpleITK as sitk
import numpy as np
import pandas
from sklearn.decomposition import PCA

import utilities as utils


class PCASkullReconstructor:
    def __init__(self, df_train=None, df_test=None):
        self.pca = PCA()
        if not df_test and not df_train:
            self.df_train, self.df_test = pandas.DataFrame(), pandas.DataFrame()
            self.sitk_train, self.sitk_test = [], []
            self.np_train_r = []
            self.np_test_r = []
            self.im_dims = []
        elif df_test and df_train:
            self.set_files(df_train, df_test)
            self.load_imgs()
            self.conv_sitk_np()
            self.fit()
            self.predict_test()
        else:
            print("Check the provided arguments")

    def set_files(self, train_path, test_path):
        self.df_train = pandas.read_csv(train_path)  # add path to each filename
        self.df_test = pandas.read_csv(test_path)

        print("Training images: ", self.df_train.shape[0])
        print("Test images: ", self.df_test.shape[0])

    def load_imgs(self):
        # Load SimpleITK images
        self.sitk_train = [sitk.ReadImage(self.df_train.iloc[i, 0]) for i in range(self.df_train.shape[0])]
        self.sitk_test = [sitk.ReadImage(self.df_test.iloc[i, 0]) for i in range(self.df_test.shape[0])]

    def conv_sitk_np(self):
        self.np_train_r = np.array([sitk.GetArrayFromImage(self.sitk_train[i]) for i in range(self.df_train.shape[0])])
        self.np_test_r = np.array([sitk.GetArrayFromImage(self.sitk_test[i]) for i in range(self.df_test.shape[0])])
        self.im_dims = self.np_train_r.shape[1:]  # Image dimensions (eg 80, 106, 106)

        # I must reshape because scikit-learn only allows 2D (index, image).
        self.np_train_r = [np.reshape(self.np_train_r[i], (np.prod(self.im_dims))) for i in range(self.df_train.shape[0])]
        self.np_test_r = [np.reshape(self.np_test_r[i], (np.prod(self.im_dims))) for i in range(self.df_test.shape[0])]

    def fit(self):
        self.pca.fit(self.np_train_r)

    def save_eig(self, n_comp=None):
        n_comp = self.pca.n_components_ if not n_comp else n_comp
        eigen = self.pca.components_.reshape((self.pca.n_components_,
                                                    self.im_dims[0], self.im_dims[1], self.im_dims[2]))

        for i in range(n_comp):
            sitk.Show(sitk.GetImageFromArray(eigen[i]))

    def predict_test(self):
        Y_pca = self.pca.transform(self.np_test_r)  # Get coefficients in th projected space
        pred_pca = self.pca.inverse_transform(Y_pca)  # Go back to the original space from the projected one

        pred_pca = pred_pca.reshape((pred_pca.shape[0], self.im_dims[0], self.im_dims[1], self.im_dims[2]))

        for i, pred in enumerate(pred_pca):
            sitk_pred = sitk.GetImageFromArray(pred) > 0.5
            sitk_pred.SetOrigin(self.sitk_test[i].GetOrigin())
            sitk_pred.SetDirection(self.sitk_test[i].GetDirection())
            sitk_pred.SetSpacing(self.sitk_test[i].GetSpacing())

            path, name = os.path.split(self.df_test.iloc[i, 0])
            path = os.path.join(path, 'pred_PCA')
            if not os.path.exists(path):
                os.makedirs(path)

            name_out = name.replace(".nii.gz", "_pca.nii.gz".format(i))
            sitk.WriteImage(sitk_pred, os.path.join(path, name_out))  # Save PCA prediction

            sitk_input_img = sitk.GetImageFromArray(self.np_test_r[i].reshape((self.im_dims[0], self.im_dims[1], self.im_dims[2])))  # Input image
            sitk_input_img.SetOrigin(self.sitk_test[i].GetOrigin())
            sitk_input_img.SetDirection(self.sitk_test[i].GetDirection())
            sitk_input_img.SetSpacing(self.sitk_test[i].GetSpacing())

            sitk_diff = utils.diff_sitk(sitk_input_img, sitk_pred)  # Difference
            sitk_diff_eroded = utils.erode(sitk_diff)  # Erode
            sitk_diff_cc = utils.get_largest_cc(sitk_diff)

            sitk.WriteImage(sitk_diff, os.path.join(path, name_out.replace('pca', 'pca_diff')))  # Save diff
            sitk.WriteImage(sitk_diff_eroded,
                            os.path.join(path, name_out.replace('pca', 'pca_diff_eroded')))  # Save eroded
            sitk.WriteImage(sitk_diff_cc, os.path.join(path, name_out.replace('pca', 'pca_diff_cc')))  # Save eroded

            print("  Saved: {}.".format(name_out))


def try_pca():
    train_f = 'splits/191223cr-rec/files_train.csv'  # Train files
    test_f = '../image/normal/clip90-91_sp2-2-2-rigid/scr200302/test_simulated.csv'  # Test files

    PCASkullReconstructor(train_f, test_f)


if __name__ == '__main__':
    try_pca()
