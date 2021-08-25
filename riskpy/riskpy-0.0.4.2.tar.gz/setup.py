from setuptools import setup, find_packages

setup(
    name='riskpy',
    version='0.0.4.2',
    description="Risk-manager\'s pack",
    url='http://google.com',
    author='Igor Shcherbakov',
    author_email='pimanov.d@gmail.com',
    license='MIT',
    packages=find_packages(),
    keywords=['modeling', 'risks', 'statistics'],  # arbitrary keywords
    zip_safe=False,
    test_suite='tests',
    install_requires=[
        'numpy==1.18.5',
        'pandas==0.25.3',
        'scikit-learn==0.21.3',
        'matplotlib==2.0.2',
        'statsmodels==0.11.1',
        'seaborn==0.7.1',
        'scipy==1.4.1'

    ]
)

