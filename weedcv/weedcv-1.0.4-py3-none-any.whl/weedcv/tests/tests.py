# import os
# import unittest
# from pathlib import Path

# import cv2
# from weedcv.classes import Params as params
# from weedcv.weedcv.clear_edges import clear_edges
# from weedcv.weedcv.load_img import load_img
# from weedcv.weedcv.make_exg import make_exg
# from weedcv.weedcv.otsu_thresh import otsu_thresh

# from weedcv.weedcv.morph_close import morph_close
# from weedcv.weedcv.filter_components import filter_components

# TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
# TEST_INPUT_EXAMPLE = str(Path(TEST_DATA, "palmer_residue_overhead_001.JPG"))
# TEST_EXAMPLE_DIM = (6000, 4000, 3)


# class Test(unittest.TestCase):
# def test_load_img(self):
# params.debug = None
# img, path = load_img(TEST_INPUT_EXAMPLE, mode="rgb")
# if img is None:
# raise AssertionError("Image is None")
# elif not Path(path).is_file():
# raise AssertionError("File does not exist: %s" % str(path))

# def test_make_exg(self):
# params.debug = None
# img = cv2.imread(TEST_INPUT_EXAMPLE)
# rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# exg = make_exg(rgb_img, exg_thresh=0)
# if exg is None:
# raise AssertionError("ExG is None")

# def test_otsu_thresh(self):
# params.debug = None
# img = cv2.imread(TEST_INPUT_EXAMPLE)
# rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# exg = make_exg(rgb_img, exg_thresh=0)
# otsu = otsu_thresh(exg)
# if otsu is None:
# raise AssertionError("OTSU is None")

# def test_clear_edges(self):
# params.debug = None
# img = cv2.imread(TEST_INPUT_EXAMPLE)
# rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# exg = make_exg(rgb_img, exg_thresh=0)
# otsu = otsu_thresh(exg)
# res = clear_edges(otsu)
# if res is None:
# raise AssertionError("Clear_edges result is None")

# def test_morph_close(self):
#     params.debug = None
#     img = cv2.imread(TEST_INPUT_EXAMPLE)
#     rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     exg = make_exg(rgb_img, exg_thresh=0)
#     otsu = otsu_thresh(exg)
#     res = clear_edges(otsu)
#     morph = morph_close(res, 500, 500)
#     if morph is None:
#         raise AssertionError("Morph_close result is None")

# def test_filter_components(self):
#     params.debug = None
#     img = cv2.imread(TEST_INPUT_EXAMPLE)
#     rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     exg = make_exg(rgb_img, exg_thresh=0)
#     otsu = otsu_thresh(exg)
#     res = clear_edges(otsu)
#     morph = morph_close(res, 500, 500)
#     filtered = filter_components(morp, 1)
#     if filtered is None:
#         raise AssertionError("Filtered result is None")


# if __name__ == "__main__":
# unittest.main()
