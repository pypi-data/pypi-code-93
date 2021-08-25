import glob
import os


class TestExamples:
  def test_jupyter_examples(self):
    example_notebooks = glob.glob('../examples/*.ipynb')
    for nb in example_notebooks:
      path = nb.replace('/', os.path.sep)
      assert os.system(f'jupyter nbconvert --to notebook --execute "{path}"') == 0, \
             f'error in {nb}'
      os.remove(path.replace('.ipynb', '.nbconvert.ipynb'))
