from distutils.core import setup
setup(
  name = 'facegrid',
  packages = ['facegrid'],
  version = '0.1.2',   
  license='MIT',
  description = 'Python package for face biometrics and other tools',
  author = 'Adithya Kurien Peter',
  author_email = 'adithya.kurien@gmail.com',
  url = 'https://github.com/aaadddiii/facegrid',
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'opencv-python',
          'mtcnn',
          'tensorflow',
          'keras_applications',
          'scipy',
      ],
  classifiers=[  
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)